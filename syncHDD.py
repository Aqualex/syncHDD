###############################################################################
##       Author: A.D.
##         Year: 2019
##        Month: November
##  Description: This script is meant to update the HDD given the location from 
##               the HDD needs to be synced and where it should copy the files. 
##               The script will check how much space is on the external HDD 
##               will create a folder with today's date and copy the files in 
##               that folder 
## 
###############################################################################

###############################################################################
##     IMPORT UTILITIES  
###############################################################################

import os                                                                      
import math                                                                     
import datetime                                                                 
from distutils.dir_util import copy_tree
from distutils.dir_util import remove_tree
import sys 
import shutil

os.environ['SYNCHDD_DAYS_KEEP'] = '2'

###############################################################################
##     DEFINING FUNCTIONS
############################################################################### 
def hdfooter(vr):
	if(vr == 'header'):
		print('')
		print('========== STARTING FUNCTION ==========')
		print('')
	else:
		print('')
		print('========== **ENDING FUNCTION ==========')
		print('')

def getTimestamp():
    return datetime.datetime.now().strftime("%Y.%m.%dD%H.%M.%S.%f")  

def getDate():
    return datetime.datetime.now().strftime("%Y.%m.%d")

def createLogMessage(lvl,message):
    if (lvl == 0): 
        prefix = "[*INFO]|"
    elif (lvl == 1):
        prefix = "[ERROR]|"
    else:
        prefix = "[DEBUG]|"
    return prefix + getTimestamp() + "| " + message 
        
def log(lvl,message):
    #create log file in specified location 
    if 'SYNCHDD_LOG' in os.environ :
        logFilePath = os.getenv("SYNCHDD_LOG")
    else:
        logFilePath = os.getcwd()
    logFileName = "logOutput_" + getDate() + ".log"
    logFilePath = logFilePath + logFileName 
    if not os.path.exists(logFilePath):
        open(logFilePath,"w")
    #create log message
    message = createLogMessage(lvl,message)
    #print to file
    print(message)
    if os.path.exists(logFilePath):
        logFileHandle = open(logFilePath,"a+")
    else:
        logFileHandle = open(logFilePath,"w")
    logFileHandle.write(message)
    logFileHandle.close()

def convertBytesToMb(bytesValue):
    return bytesValue/1000000

def makeSpace(path):
	print('TEST') 

def removeDays(path):
	# check if SYNCHDD_DAYS_KEEP is defined and only keep the data copied for 
	# thos days 
	if 'SYNCHDD_DAYS_KEEP' in os.environ: 
		log(0,"removeDays: Removing data older than " + os.getenv('SYNCHDD_DAYS_KEEP') + " days ...")
		#print(os.listdir(path))
		dt = os.listdir(path)
		#threshold = int(os.environ('SYNCHDD_DAYS_KEEP'))
		#print(threshold)
		thresholdDate = (datetime.datetime.today() - datetime.timedelta(days = int(os.getenv('SYNCHDD_DAYS_KEEP')))).strftime('%Y.%m.%d')
		#print(type(thresholdDate))
		for i in dt: 
			#print('date is ' + i)
			#print(datetime.datetime.strptime(i,'%Y.%m.%d'))
			if (datetime.datetime.strptime(i,'%Y.%m.%d') < datetime.datetime.strptime(thresholdDate,"%Y.%m.%d")):
				print(i)
				print(path + i + "/")
				try:
					remove_tree(path + i + "/")
				except OSError as e: 
					log(1,"removeDays: Failed to delete directory [" + (path + i + "/") + "] with error: " + e)

def getNecessarySpace(path):
    log(0,"getNecessarySpace: Getting necessary space ...")
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return math.ceil(convertBytesToMb(total_size))
    
def getAvailableSpace(path):
    log(2,"getAvailableSpace: Getting available space ...")
    return math.ceil(convertBytesToMb(os.statvfs(path).f_frsize * os.statvfs(path).f_bavail))
    
def createTodayFolder(path):
    folderName = datetime.datetime.now().strftime("%Y.%m.%d")
    #list folder in directory and check if fodler for today already exists 
    if not folderName in os.listdir(path) :
        log(0,"createTodayFolder: Creating folder: " + folderName + " in " + path)
        try:
            os.mkdir(path + folderName)
        except OSError:
            log(2,"createTodayFolder: Failed to create folder " + folderName + " in " + path)
        else:
            log(0,"createTodayFolder: Successfully created folder " + folderName + " in " + path)
    else:
        log(1,"createTodayFolder: Folder already exists ...")
    return folderName
    
def copyFilesAccross(source,destination):
    #check if there is enough space
    log(0,"copyFilesAccross: Copying files ...")
    try:
        copy_tree(source,destination)
    except OSError as e:
        log(1,"copyFileAccross: Failed to copy from " + source + " to " + destination + " with error: " + e)
    
def checkEnvVar(eV):
    for v in eV: 
        if os.getenv(v) is None: 
            log(1,'checkEnvVar: Environment variable: ' + v + ' has not been set. Function will terminate ...')
            sys.exit()
    
def main():
	#hdfooter('header')
	#checkEnvVar(["SYNCHDD_FROM","SYNCHDD_TO","SYNCHDD_LOG"])
	source = os.getenv("SYNCHDD_FROM")
	destination = os.getenv("SYNCHDD_TO")
	removeDays(destination)
	#log(0,"main: Moving from " + source + " to " + destination)
    #create folder with today's date 
	destination = destination + createTodayFolder(destination)
	#if(getNecessarySpace(source) > getAvailableSpace(destination)):
	#	log(1,"main: Needed space is greater than available space. Necessary: " 
    #        + str(getNecessarySpace(source)) 
    #        + " Available: " 
    #        + str(getAvailableSpace(destination)))
	#else:
	#	log(0,"main: There is enough space. Files can be copied")
	#	copyFilesAccross(source,destination)
	#hdfooter('footer')
        
###############################################################################
##     MAIN 
###############################################################################

main()
