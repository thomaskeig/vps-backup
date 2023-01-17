import yaml
import os
import shutil
import datetime

with open('./settings.yml', encoding="utf8") as file:
    try:
        global settings
        settings = yaml.load(file, Loader=yaml.FullLoader)
        print('Successully Loaded Settings\n')
    except:
        print('An unknown error occured whilst loading settings\n')

for backupInfo in settings['backups']:

    x = datetime.datetime.now()
    currentDate = str(x.strftime(settings["file-name"]))

    print(f'Creating Archive for {backupInfo["zip-identifier"]}')
    
    shutil.make_archive(f'/root/temp/{currentDate}-{backupInfo["zip-identifier"]}', 'zip', backupInfo["directory"])

    print('Uploading zip...')

    os.system(f'rclone copy "/root/temp/{currentDate}-{backupInfo["zip-identifier"]}.zip" "uwe-onedrive:/VPS Backups/{backupInfo["zip-identifier"]}"')

    print('Done!')

    # Remove temporary zip file
    os.remove(f'/root/temp/{currentDate}-{backupInfo["zip-identifier"]}.zip')

    print('Successfully deleted temporary file')