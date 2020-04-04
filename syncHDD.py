###############################################################################
##       Author: A.D.
##         Year: 2020
##        Month: April
##  Description: This script is meant to update the HDD given the location from 
##               the HDD needs to be synced and where it should copy the files. 
##               The script will check how much space is on the external HDD 
##               will create a folder with today's date and copy the files in 
##               that folder 
## 
## Example Call: python3 syncHDD.py -SYNCHDD_DAYS_KEEP [integer] 
##                                  -SYNCHDD_FROM [path] 
##                                  -SYNCHDD_TO [path] 
##                                  -SYNCHDD_LOG [path]
##
###############################################################################

###############################################################################
##     IMPORT UTILITIES  
###############################################################################
import os  
import re                                                                      #to use the match capabilities in python                                                                 
import math                                                                     
import datetime                                                                 
from distutils.dir_util import copy_tree
from distutils.dir_util import remove_tree
import sys, getopt

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
        
def openCloseLogFile(action,file=None):
    #function to open the logfile and print the header and footer 
    #create log file in specified location 
    if 'SYNCHDD_LOG' in os.environ :
        logFilePath = os.getenv("SYNCHDD_LOG")
    else:
        logFilePath = os.getcwd()
    logFileName = "logOutput_" + getDate() + ".log"
    logFilePath = logFilePath + logFileName 
    if action == "open":
        if os.path.exists(logFilePath):
            #if file exists open to append new log messages
            file = open(logFilePath,"a+")
            file.write('========== STARTING FUNCTION ==========\n')
            return file
        else:
            #if files does not exist, create it.
            file = open(logFilePath,"w")
            file.write('========== STARTING FUNCTION ==========\n')            
            return file
    else:
        file.write('========== **ENDING FUNCTION ==========\n\n')
        file.close()
    
def log(lvl,message,file):
    #create log message
    message = createLogMessage(lvl,message)
    #print to file
    print(message)
    file.write(message)
    file.write('\n')

def convertBytesToMb(bytesValue):
    return bytesValue/1000000

def return_date_like_folders(fld):
    res = []
    for fname in fld: 
        if (re.match(r"\d+\.\d+\.\d+", fname)):
            res.append(fname)
    return res

def makeSpace(path):
	print('TEST') 

def removeDays(path,file):
	# check if SYNCHDD_DAYS_KEEP is defined and only keep the data copied for 
	# thos days 
	if 'SYNCHDD_DAYS_KEEP' in os.environ: 
		log(0,"removeDays: Removing data older than " + os.getenv('SYNCHDD_DAYS_KEEP') + " days ...",file)
		dt = return_date_like_folders(os.listdir(path))

		thresholdDate = (datetime.datetime.today() - datetime.timedelta(days = int(os.getenv('SYNCHDD_DAYS_KEEP')))).strftime('%Y.%m.%d')
		for i in dt: 
			if (datetime.datetime.strptime(i,'%Y.%m.%d') < datetime.datetime.strptime(thresholdDate,"%Y.%m.%d")):
				print(path + i + "/")
				try:
					remove_tree(path + i + "/")
				except OSError as e: 
					log(1,"removeDays: Failed to delete directory [" + (path + i + "/") + "] with error: " + e,file)

def getNecessarySpace(path,file):
    log(0,"getNecessarySpace: Getting necessary space ...",file)
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return math.ceil(convertBytesToMb(total_size))
    
def getAvailableSpace(path,file):
    log(2,"getAvailableSpace: Getting available space ...",file)
    return math.ceil(convertBytesToMb(os.statvfs(path).f_frsize * os.statvfs(path).f_bavail))
    
def createTodayFolder(path,file):
    folderName = datetime.datetime.now().strftime("%Y.%m.%d")
    #list folder in directory and check if fodler for today already exists 
    if not folderName in os.listdir(path) :
        log(0,"createTodayFolder: Creating folder: " + folderName + " in " + path,file)
        try:
            os.mkdir(path + folderName)
        except OSError:
            log(2,"createTodayFolder: Failed to create folder " + folderName + " in " + path,file)
        else:
            log(0,"createTodayFolder: Successfully created folder " + folderName + " in " + path,file)
    else:
        log(1,"createTodayFolder: Folder already exists ...",file)
    return folderName
    
def copyFilesAccross(source,destination,file):
    #check if there is enough space
    log(0,"copyFilesAccross: Copying files ...",file)
    try:
        copy_tree(source,destination)
    except OSError as e:
        log(1,"copyFileAccross: Failed to copy from " + source + " to " + destination + " with error: " + e,file)
    
def checkEnvVar(eV,file):
    for v in eV: 
        if os.getenv(v) is None:
            log(1,'checkEnvVar: Environment variable: ' + v + ' has not been set. Function will terminate ...',file)
            sys.exit()

def getProgParams(arg, parName):
    #function to check if env var are defined if not take from command line
    #env variables have priority
    if os.getenv(parName) is None:
        print('getProgParams: Environment Variable Does Not Exist -> For variable '+ parName +' setting to ' + arg)
        return arg
    else: 
        print('getProgParams: Environment Variable Exists -> For variable '+ parName +' setting to ' + os.getenv(parName))
        return os.getenv(parName)
     
def getCmdLineArguments():
    #function to create a dictionary of arguments passed from the cmdline 
    dictVal = {}                                                               #Creating an empty dictionary
    argv = sys.argv[1:]
    try:
      opts, args = getopt.getopt(argv, "hd:f:t:l:" ,["SYNCHDD_DAYS_KEEP=", "SYNCHDD_FROM=", "SYNCHDD_TO=", "SYNCHDD_LOG="])
    except getopt.GetoptError:
      print('getCmdLineArguments: Faile to get command line arguments ...')
      sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("\nHelp Message:\nsyncHDD.py --SYNCHDD_DAYS_KEEP [integer] --SYNCHDD_FROM [path] --SYNCHDD_TO [path] --SYNCHDD_LOG [path]\n")
            sys.exit()
        elif opt in ("-d", "--SYNCHDD_DAYS_KEEP"):
            dictVal['SYNCHDD_DAYS_KEEP'] = getProgParams(arg, 'SYNCHDD_DAYS_KEEP')
        elif opt in ("-f", "--SYNCHDD_FROM"):
            dictVal['SYNCHDD_FROM'] = getProgParams(arg, 'SYNCHDD_FROM')
        elif opt in ("-t", "--SYNCHDD_TO"):
            dictVal['SYNCHDD_TO'] = getProgParams(arg, 'SYNCHDD_TO')
        elif opt in ("-l", "--SYNCHDD_LOG"):
            dictVal['SYNCHDD_LOG'] = getProgParams(arg, 'SYNCHDD_LOG')
    return dictVal

def main():
    dictVal = getCmdLineArguments()
    hdfooter('header')
    file = openCloseLogFile("open")
    for elem in ['SYNCHDD_DAYS_KEEP','SYNCHDD_FROM','SYNCHDD_TO','SYNCHDD_LOG']:
        if not elem in list(dictVal.keys()):
            if os.getenv(elem) is None:
                log(1,'main: Variable '+ elem + ' is missing. Exiting ...',file)
                sys.exit(2)
            else: 
                log(0,'main: Variable '+ elem + ' will be set to ' + os.getenv(elem),file)
                dictVal[elem] = os.getenv(elem)
    ##checkEnvVar(["SYNCHDD_FROM","SYNCHDD_TO","SYNCHDD_LOG"],file)
    src = os.getenv("SYNCHDD_FROM")
    destination = dictVal['SYNCHDD_TO']
    removeDays(destination,file)
    log(0,"main: Moving from " + src + " to " + destination,file)
    #create folder with today's date 
    destination = destination + createTodayFolder(destination,file)
    if(getNecessarySpace(src,file) > getAvailableSpace(destination,file)):
        log(1,"main: Needed space is greater than available space. Necessary: " 
            + str(getNecessarySpace(src,file)) 
            + " Available: " 
            + str(getAvailableSpace(destination,file)))
    else:
            log(0,"main: There is enough space. Files can be copied",file)
            copyFilesAccross(src,destination,file)
    
    openCloseLogFile("close",file)
    hdfooter('footer')
        
###############################################################################
##     MAIN 
###############################################################################

main()
