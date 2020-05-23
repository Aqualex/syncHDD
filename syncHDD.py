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
## Example Call: python3 syncHDD.py --SYNCHDD_DAYS_KEEP [integer] 
##                                  --SYNCHDD_FROM [path] 
##                                  --SYNCHDD_TO [path] 
##                                  --SYNCHDD_LOG [path]
##
## python3 syncHDD.py --SYNCHDD_DAYS_KEEP 5 --SYNCHDD_FROM /media/alex/cf35aee0-faeb-40bb-adac-88595e8f71fe/alex_hdd/2020/github/syncHDD/from_testing_dir/ --SYNCHDD_TO /media/alex/d18fd2c4-f431-4a18-b5b1-83515df335fa --SYNCHDD_LOG /media/alex/cf35aee0-faeb-40bb-adac-88595e8f71fe/alex_hdd/2020/github/syncHDD/log_folder/
## python3 syncHDD.py --SYNCHDD_DAYS_KEEP 5 --SYNCHDD_FROM /media/alex/cf35aee0-faeb-40bb-adac-88595e8f71fe/alex_hdd/2020/github/syncHDD/scenario2_morelocation/location_one/ /media/alex/cf35aee0-faeb-40bb-adac-88595e8f71fe/alex_hdd/2020/github/syncHDD/scenario2_morelocation/location_two/ --SYNCHDD_TO /media/alex/d18fd2c4-f431-4a18-b5b1-83515df335fa --SYNCHDD_LOG /media/alex/cf35aee0-faeb-40bb-adac-88595e8f71fe/alex_hdd/2020/github/syncHDD/log_folder/
##
###############################################################################

###############################################################################
##     IMPORT UTILITIES  
###############################################################################
import importlib, sys

for moduleName in ['os', 're', 'math', 'datetime', 'distutils', 'sys', 'getopt', 'crontab', 'getpass']: 
    #print('Importing ' + moduleName + " ... ", end="")
    try: 
        globals()[moduleName] = importlib.import_module(moduleName)
    except ModuleNotFoundError: 
       print('FAILED to import module ' + moduleName)
       sys.exit()

from distutils import dir_util

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

def sep():
    if sys.platform.startswith('linux'):
        return '/'
    if sys.platform.startswith('win'):
        return '\\'

def createLogMessage(lvl,message):
    if (lvl == 0): 
        prefix = "[*INFO]|"
    elif (lvl == 1):
        prefix = "[ERROR]|"
    else:
        prefix = "[DEBUG]|"
    return prefix + getTimestamp() + "| " + message 
        
def openCloseLogFile(LFN, dV, action,file=None):
    #function to open the logfile and print the header and footer 
    #create log file in specified location 
    logFilePath = dV['SYNCHDD_LOG']
    logFilePath = logFilePath + "/" + LFN 
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
	return (bytesValue/1000000.0)/1024.0

def return_date_like_folders(fld):
    res = []
    for fname in fld: 
        if (re.match(r"\d+\.\d+\.\d+", fname)):
            res.append(fname)
    return res

def removeDays(path,dV,file):
	# check if SYNCHDD_DAYS_KEEP is defined and only keep the data copied for 
	# thos days 
	startTime = datetime.datetime.now()
	log(0,"removeDays: Removing data older than " + dV['SYNCHDD_DAYS_KEEP'] + " days from " + path,file)
	dt = return_date_like_folders(os.listdir(path))
	thresholdDate = (datetime.datetime.today() - datetime.timedelta(days = int(dV['SYNCHDD_DAYS_KEEP']))).strftime('%Y.%m.%d')
	for i in dt: 
		if (datetime.datetime.strptime(i,'%Y.%m.%d') < datetime.datetime.strptime(thresholdDate,"%Y.%m.%d")):
			try:
				log(0, "removeDays: Attempting to remove: " + path + i + "/", file)
				dir_util.remove_tree(path + i + "/")
			except OSError as e: 
				log(1,"removeDays: Failed to delete directory [" + (path + i + "/") + "] with error: " + e,file)

def getNecessarySpace(path,file):
    log(0,"getNecessarySpace: Getting necessary space for " + path,file)
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return convertBytesToMb(total_size)
    
def getAvailableSpace(path,file):
    #log(2,"getAvailableSpace: Getting available space ...",file)
    return convertBytesToMb(os.statvfs(path).f_frsize * os.statvfs(path).f_bavail)
    
def createTodayFolder(dictVal, logFileName, path,file):
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
        log(1,"createTodayFolder: Folder already exists. Program will now terminate.",file)
        openCloseLogFile(logFileName, dictVal, "close", file) 
        hdfooter('footer')
        sys.exit()
    return folderName
    
def copyFilesAccross(source, destination, file):
    #check if there is enough space
    startTime = datetime.datetime.now()
    log(0,"copyFilesAccross: Copying files ...",file)
    try:
        dir_util.copy_tree(source,destination)
        log(0,"copyFilesAccross: Operation has completed successfully in: " + str(datetime.datetime.now() - startTime), file)
    except OSError as e:
        log(1,"copyFileAccross: Failed to copy from " + source + " to " + destination + " with error: " + e,file)

def getProgParams(arg, parName):
    #function to check if env var are defined if not take from command line
    #env variables have priority
    if os.getenv(parName) is None:
        #print('getProgParams: Environment Variable Does Not Exist -> For variable '+ parName +' setting to ' + arg)
        return arg
    else: 
        #print('getProgParams: Environment Variable Exists -> For variable '+ parName +' setting to ' + os.getenv(parName))
        return os.getenv(parName)
     
def getCmdLineArguments():
    #function to create a dictionary of arguments passed from the cmdline 
    dictVal = {}                                                               #Creating an empty dictionary
    argv = sys.argv[1:]
    dictVal['execLine'] = ' '.join([sys.executable] + [os.getcwd() + sep() + sys.argv[0]] + argv)
    try:
      opts, args = getopt.getopt(argv, "hd:f:t:l:" ,["SYNCHDD_DAYS_KEEP=", "SYNCHDD_FROM=", "SYNCHDD_TO=", "SYNCHDD_LOG="])
    except getopt.GetoptError:
      print('getCmdLineArguments: Failed to get command line arguments ...')
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

def addToCron(eL, dV, file):
    #there are some errors in here that I need to sort out
    #seems to add the jobs quite a few times 
    #also seems to change the scheduling for other jobs 
    #function to add this job to the cron job if on linux
    log(0,'addToCron: Attempting to add a new job to cron',file)
    myCron = crontab.CronTab(user = getpass.getuser()) 
    scriptName = dV['execLine'].split(' ')[1].split('/')[-1]
    jobExists = False
    for job in myCron:
        if job.comment == scriptName:
            jobExists = not jobExists
    if not jobExists:
        log(0,'addToCron: Adding ' + dV['execLine'] + ' to crontab ...',file)
        job = myCron.new(command = dV['execLine'], comment='syncHDD.py')
        job.hour.on(23)
        try: 
            myCron.write()
            log(0,'Job has been successfully added to crontab ',file)
        except OSError as errorMessage: 
            log(1,'addToCron: Failed to write to crontab with OSError -> ' + str(errorMessage), file)
    else:
        log(1,'addToCron: Job ['+ scriptName +'] already exists',file)

def main():
	startTime = datetime.datetime.now()
	dictVal = getCmdLineArguments()
	hdfooter('header')
	logFileName = "logOutput_" + datetime.datetime.now().strftime("%Y%m%dD%H%M%S%f") + ".log"
	file = openCloseLogFile(logFileName, dictVal, "open")
	log(0,"Log messages will be printed in: " + logFileName,file)
	for elem in ['SYNCHDD_DAYS_KEEP','SYNCHDD_FROM','SYNCHDD_TO','SYNCHDD_LOG']:
		if not elem in list(dictVal.keys()):
			if os.getenv(elem) is None:
				log(1,'main: Variable '+ elem + ' is missing. Exiting ...',file)
				sys.exit(2)
			else: 
				log(0,'main: Variable '+ elem + ' will be set to ' + os.getenv(elem),file)
				dictVal[elem] = os.getenv(elem)

	src = dictVal['SYNCHDD_FROM'].split()
	destination = dictVal['SYNCHDD_TO']
	addToCron(dictVal['execLine'], dictVal, file)
	removeDays(destination,dictVal,file)
	destination = destination + createTodayFolder(dictVal, logFileName, destination,file)
	availableSpace = getAvailableSpace(destination,file)
	necessarySpace = 0 
	for frm in src: 
		necessarySpace += getNecessarySpace(frm,file)
	if( necessarySpace > availableSpace):
		log(1,"main: Needed space is greater than available space. Necessary: " 
			+ str(round(necessarySpace,2)) + " GB" 
			+ " Available: " 
			+ str(round(availableSpace,2)) + " GB",file)
	else:
		log(0,"main: Available space: " + str(round(availableSpace,2)) + " GB" + " Necessary space: " + str(round(necessarySpace,2)) + " GB", file)
		log(0,"main: There is enough space. Files can be copied",file)
		for frm in src:
			log(0,"main: Moving from " + frm + " to " + destination,file)
			copyFilesAccross(frm,destination,file)

	log(0,"main: Operation took: " + str(datetime.datetime.now() - startTime),file)
	openCloseLogFile(logFileName, dictVal, "close", file)
	hdfooter('footer')
        
###############################################################################
##     MAIN 
###############################################################################

main()
