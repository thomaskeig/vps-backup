try:
    import os
    import shutil
    import datetime
    import traceback

    os.system("chmod u+x /root/backup/rclone")

    dirList = os.listdir('/var/lib/pterodactyl/volumes')

    for itemName in dirList:
        
        x = datetime.datetime.now()
        currentDate = str(x.strftime("%Y-%m-%d")) # %Y-%m-%d-%H-%M-%S
            
        shutil.make_archive(f'/root/temp/{currentDate}/{itemName}', 'zip', f'/var/lib/pterodactyl/volumes/{itemName}')
            
        os.system(f'/root/backup/rclone copy "/root/temp/{currentDate}/{itemName}.zip" "uwe-onedrive:/Pterodactyl Backups/{currentDate}" -P')

        os.system(f'rm -r /root/temp/{currentDate}')

except Exception as e:
    with open("/root/backup/error.txt", "a") as file:
        file.write("Error occurred:\n")
        file.write(str(e))
        file.write("\n")
        traceback.print_exc(file=file)
