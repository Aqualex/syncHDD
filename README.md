
# syncHDD 

## Description 
I had a simple problem -> periodically copy a number of files from my local machine to an external HDD
It should have been a simple task, but after starting to type some code to see how it works I started getting few ideas to improve the script: 

 1. Script should write permanently and check if the external HDD is connected
 2. When HDD connected check if today's date exists and if not, start copying the files across
 3. Before copying, check if old days are present and delete those to free space
 4. Check to see if the external HDD has enough space to copy the files across
 5. When copying the files allow for new file/folder names or zipping the files and folders if necessary
 6. Add the job to cron with a @reboot tag to start the scrip after system reboot

## Environment Variables 
* **SYNCHDD\_DAYS\_KEEP**        - number of days you want to keep on your hdd
* **SYNCHDD\_TARGET**            - the path to the device where files should be copied
* **SYNCHDD\_INSTRUCTION\_FILE** - the path to the csv file containing instructions for the transfer
* **SYNCHDD\_ADD\_TO\_CRON**     - True/False, if script should be added to cron to start on boot


## Startup Example 
```
python3 -u <path>/syncHDD.py
        --SYNCHDD_DAYS_KEEP 7 --SYNCHDD_TARGET <path_to_device>\
        --SYNCHDD_INSTRUCTION_FILE <path>/zippingInstructions.csv\
        --SYNCHDD_ADD_TO_CRON True >> /tmp/syncHDD_test.log 2>&1
```
