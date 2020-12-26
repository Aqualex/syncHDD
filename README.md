# syncHDD 

## Description 
This script is used to update, on a schedule, an external HDD used for back-up. The script takes one or a list of location from which it will copy to one destination. The script will check the destination HDD to see if a folder with current date already exists and if not it creates the date folder in the format YYYY.MM.DD. The script will remove the days older than SYNCHDD\_DAYS\_KEEP and check if there is enough space on the disk to copy the files. If not, script will exit. If space is sufficient, script will be added to cron and proceed to copy files across. 

## Environment Variables 
* **SYNCHDD\_DAYS\_KEEP** - number of days you want to keep on your hdd
* **SYNCHDD\_FROM**       - destination from where to copy the files 
* **SYNCHDD\_TO**         - destination where files will ne copied 
* **SYNCHDD\_LOG**        - the location of the log file 
* **verbose**             - if set to 0 only outputs errors otherwise outputs everything

## Startup Example 
```python3 syncHDD.py --SYNCHDD_DAYS_KEEP 7 --SYNCHDD_FROM="path/one path/two" --SYNCHDD_TO path/to --SYNCHDD_LOG path/logFile --verbose 1```  
