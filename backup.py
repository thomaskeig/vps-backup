import yaml
import os
import shutil
import datetime
import json
import asyncio
import time
from datetime import datetime

import discord
from discord.ext import commands, tasks

with open('./settings.yml', encoding="utf8") as file:
    try:
        global settings
        settings = yaml.load(file, Loader=yaml.FullLoader)
        print('Successully Loaded Settings\n')
    except:
        print('An unknown error occured whilst loading settings\n')

intents = discord.Intents.default()
# intents.members = True
# intents.message_content = True

bot = discord.Bot(debug_guilds=[settings["main-server-id"]], intents=intents)

@bot.event
async def on_ready():

    update_status.start()

    autobackup.start() # Automatically backup every x time

    print(f'Successfully Logged in as {bot.user}')

@tasks.loop(seconds=10)
async def update_status():

    with open('./history.json', "r") as f:
        data = json.load(f)

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{data["backups-completed"]} Backups'))

    await asyncio.sleep(120)

def addBackupCount():
    with open('./history.json', "r") as f:
        data = json.load(f)
    
    data["backups-completed"] += 1

    with open('./history.json', "w") as f:
        json.dump(data, f, indent=4)
    
# ---------------------- #
# ---------------------- #
# ---------------------- #

@bot.command(name='backup', description = 'Force a VPS backup')
async def profile(ctx):

    if ctx.author.id != int(settings['owner-id']):
        await ctx.respond(embed=discord.Embed(description='<:caution:1063940211140206653> You are not the bot owner and cannot perform this command!', color=0x78a7ff))
    else:
        await ctx.defer()
        await backup()
        completed_embed = discord.Embed(description=f'<:tick:1053113416966996009> Backup completed! Please see <#{settings["log-channel"]}> for the overview', color=0x78a7ff)
        await ctx.respond(embed=completed_embed)
    
async def backup():

    status_message = ''

    start_time = round(time.time())

    for backupInfo in settings['backups']:
        
        create_zip_status = False
        try:
            x = datetime.datetime.now()
            currentDate = str(x.strftime(settings["file-name"]))
            
            shutil.make_archive(f'/root/temp/{currentDate}-{backupInfo["zip-identifier"]}', 'zip', backupInfo["directory"])
            file_stats = os.stat(f'/root/temp/{currentDate}-{backupInfo["zip-identifier"]}.zip')
            create_zip_status = True

        except Exception as e:
            create_zip_status = e


        upload_zip_status = False
        try:
            os.system(f'rclone copy "/root/temp/{currentDate}-{backupInfo["zip-identifier"]}.zip" "uwe-onedrive:/VPS Backups/{backupInfo["zip-identifier"]}" -P')

            upload_zip_status = True

        except Exception as e:
            upload_zip_status = e


        remove_zip_status = False
        try:
            os.remove(f'/root/temp/{currentDate}-{backupInfo["zip-identifier"]}.zip')
            remove_zip_status = True

        except Exception as e:
            remove_zip_status = e
        
        file_size_mb = round(file_stats.st_size / (1024 * 1024), 1)
        
        status_message = status_message + f'__**{backupInfo["zip-identifier"]}**__ `{file_size_mb} MB`\n'
        if create_zip_status == True:
            status_message = status_message + '<:tick:1053113416966996009> Created ZIP\n'
        else:
            status_message = status_message + f'<:caution:1063940211140206653> Failed to Create ZIP ({create_zip_status})\n'

        if upload_zip_status == True:
            status_message = status_message + '<:tick:1053113416966996009> Uploaded ZIP to Onedrive\n'
        else:
            status_message = status_message + f'<:caution:1063940211140206653> Failed to Upload ZIP ({upload_zip_status})\n'

        if remove_zip_status == True:
            status_message = status_message + '<:tick:1053113416966996009> Deleted ZIP\n\n'
        else:
            status_message = status_message + f'<:caution:1063940211140206653> Failed to Delete ZIP ({remove_zip_status})\n\n'
    
    end_time = round(time.time())

    status_message = status_message + f'<:star:1053086176136925194> Time Taken: **{end_time - start_time} Seconds**'
    
    addBackupCount() # Add one to the backup counter

    embed = discord.Embed(description=f'<:cloud:1063940216202727454> **BACKUP COMPLETED**\n<:reply:1042577160164098189> <t:{round(time.time())}>\n\n' + status_message, color=0x78a7ff)
    embed.set_footer(text='https://github.com/thomaskeig/vps-backup', icon_url=bot.user.avatar.url)
    
    channel = bot.get_channel(int(settings['log-channel']))
    await channel.send(embed=embed)

    print(f'Completed a backup → {currentDate}')





@tasks.loop(hours=24)
async def autobackup():

    dt = datetime.now()
    day_of_week = dt.weekday()

    if day_of_week in settings['schedule']['days-of-week']:
        await backup()


@autobackup.before_loop
async def wait_until_autobackup():
    now = datetime.datetime.now().astimezone()
    next_run = now.replace(
        hour=int(settings['schedule']['hour']),
        minute=int(settings['schedule']['minute']),
        second=0
        )
    if next_run < now:
        next_run += datetime.timedelta(days=1)
    await discord.utils.sleep_until(next_run)

bot.run(settings['bot-token'])