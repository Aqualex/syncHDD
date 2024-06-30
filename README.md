# syncHDD 

## Description 
I had a simple problem: periodically copy a number of files from my local machine to an external HDD. 

## Environment Variables 
* **SYNCHDD\_DAYS\_KEEP**        - number of days you want to keep on your hdd
* **SYNCHDD\_TARGET**            - the path to the device where files should be copied
* **SYNCHDD\_INSTRUCTION\_FILE** - the path to the csv file containing instructions for the transfer
* **SYNCHDD\_ADD\_TO\_CRON**     - True/False, if script should be added to cron to start on boot


## Startup Example 
```python3 syncHDD.py --SYNCHDD_DAYS_KEEP 7 --SYNCHDD_FROM="path/one path/two" --SYNCHDD_TO path/to --SYNCHDD_LOG path/logFile --verbose 1```  
