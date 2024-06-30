####################################################################################################
# Author: A.D.
# Year: 2024
# Month: April
#
# Description: This script is meant to update the HDD given the location from
#                the HDD needs to be synced and where it should copy the files.
#              The script will check how much space is on the external HDD
#                will create a folder with today's date and copy the files in
#                that folder
##
# Example Call: python3 syncHDD.py --SYNCHDD_DAYS_KEEP [integer]
# --SYNCHDD_INSTRUCTION_FILE [path as space delimtied string]
# --SYNCHDD_TARGET [path]
# 
# CMD Line: 
# python3 -u path/syncHDD.py 
#         --SYNCHDD_DAYS_KEEP 7 --SYNCHDD_TARGET path_to_device 
#         --SYNCHDD_INSTRUCTION_FILE path_to_csv.csv 
#         --SYNCHDD_ADD_TO_CRON True >> /tmp/syncHDD_test.log 2>&1
##
##
####################################################################################################

####################################################################################################
# IMPORT UTILITIES
####################################################################################################
import distutils.dir_util
import sys
import os 
import datetime 
import getopt
import shutil
import zipfile
import psutil
import time
import distutils
import pandas as pd

from crontab import CronTab

####################################################################################################
# DEFINING CLASSES
####################################################################################################
class Switcher(object):
    def getMethod(self, prm, dv):
        method = getattr(self, prm, '')
        return method(dv)

    def SYNCHDD_DAYS_KEEP(self, dv):
        return ' --SYNCHDD_DAYS_KEEP ' + str(dv['SYNCHDD_DAYS_KEEP'])

    def SYNCHDD_INSTRUCTION_FILE(self, dv):
        return ' --SYNCHDD_INSTRUCTION_FILE ' + str(dv['SYNCHDD_INSTRUCTION_FILE'])

    def SYNCHDD_TARGET(self,dv):
        return ' --SYNCHDD_TARGET ' + str(dv['SYNCHDD_TARGET'])
    
    def SYNCHDD_ADD_TO_CRON(self,dv):
        return ' --SYNCHDD_ADD_TO_CRON ' + str(dv['SYNCHDD_ADD_TO_CRON'])

class timeTheScript:
    def __init__(self):
        self.startTime = datetime.datetime.now()

    def showTimeSpent(self):
        return datetime.datetime.now() - self.startTime

class Disk: 
    def __init__(self, dictVal):
        self.diskName = dictVal['SYNCHDD_TARGET']
        self.daysToKeep = dictVal['SYNCHDD_DAYS_KEEP']

    def checkHDDConnected(self):
        diskName = self.diskName
        allPartitions = []
        for p in psutil.disk_partitions():
            if (not p.mountpoint == '/') and (not 'snap' in p.mountpoint) and (not 'boot' in p.mountpoint): 
                allPartitions.append(p.mountpoint)
            
        if len([p for p in allPartitions if p in diskName]):
            return True
        else:
            return False

    def todayExists(self):
        if datetime.datetime.now().strftime("%Y%m%d") in os.listdir(self.diskName):
            print('Today\'s folder already exists ... ')
            return True
        else:
            return False
        
    def removeOldDays(self):
        base = datetime.datetime.today()
        datesToKeep = [(base - datetime.timedelta(days=x+1)).strftime('%Y%m%d') for x in range(int(self.daysToKeep))]
        folderList = [x for x in os.listdir(self.diskName) if not x.startswith('.')]
        toRemove = [x for x in folderList if x not in datesToKeep]

        if len(toRemove): 
            for dir in toRemove: 
                dirname = self.diskName + dir
                dirname = dirname + '/' if dirname[-1] == '/' else dirname
                try: 
                    print('Removing directory ' + dirname)
                    shutil.rmtree(dirname)
                    print('Direcotry has been removed ')
                except: 
                    print('Failed to remove directory: ' + dirname)

class processTransfer:
    def __init__(self, dictVal):
        self.instructionFile = self.getInstructionsFromFile(dictVal['SYNCHDD_INSTRUCTION_FILE'])
        self.destination = dictVal['SYNCHDD_TARGET']

    def getInstructionsFromFile(self, tDest):
        # return self.appendAvailableSpace(pd.read_csv(tDest))
        res = pd.read_csv(tDest)
        res = res[res['active'] == True]
        return res 
    
    def run(self):
        df = self.instructionFile
        df['necessarySpaceInGB'] = [None] * len(df)
 
        for index, row in df.iterrows():
            df.loc[index] = self.getNecessarySpace(row)

        availableSpace = self.getAvailableSpace(self.destination)

        nSpace = sum(list(df['necessarySpaceInGB']))

        if (nSpace >= availableSpace): 
            print('Not enough space on device to copy the files! Device: ' + dest)
        else:
            print('Space on Device [' + str(availableSpace) +'] Necessary Space [' + str(nSpace) +'] PASS')
            self.copyFiles() 

    def copyFiles(self):
        instructionFile = self.instructionFile
        crtDate = datetime.datetime.now().strftime("%Y%m%d")

        for index,row in instructionFile.iterrows():
            if os.path.isdir(row['from']):
                if pd.isna(row.newName):
                    if row.compression == 'zip': 
                        rFrom = row['from'][:-1] if row['from'][-1] == '/' else row['from']
                        newDest = self.destination + crtDate + '/' + rFrom.split('/')[-1]
                        try:
                            print('Copying ',row['from'],' to ',newDest)
                            shutil.make_archive(newDest, 'zip', row['from'])
                        except: 
                            print('Failed to copy file ' + row['from'] + ' to ' + newDest)
                    else: 
                        rFrom = row['from'][:-1] if row['from'][-1] == '/' else row['from']
                        newDest = self.destination + crtDate + '/' + rFrom.split('/')[-1] + '/'
                        try:
                            print('Copying ',row['from'],' to ',newDest)
                            distutils.dir_util.copy_tree(row['from'], newDest)
                        except: 
                            print('Failed to copy file ' + row['from'] + ' to ' + newDest)
                else: 
                    if row.compression == 'zip': 
                        newDest = self.destination + crtDate + '/' + row.newName
                        try: 
                            print('Copying ',row['from'],' to ',newDest)
                            shutil.make_archive(newDest, 'zip', row['from'])
                        except:
                            print('Failed to copy file ' + row['from'] + ' to ' + newDest)
                    else: 
                        newDirName = self.destination + crtDate + '/' + row.newName + '/'
                        os.makedirs(newDirName, exist_ok=True)
                        print('Copying folder ' + row['from'] + ' to ' + newDirName)
                        try:
                            distutils.dir_util.copy_tree(row['from'], newDirName)
                        except:
                            print('Failed to copy file ' + row['from'] + ' to ' + newDest)
            else:
                if pd.isna(row.newName):
                    if row.compression == 'zip':
                        fName = row['from'].split('/')[-1]
                        newDest = self.destination + crtDate + '/' + fName.split('.')[0] + '.zip'

                        try:
                            os.makedirs(os.path.join('/', *newDest.split('/')[:-1]), exist_ok=True)

                            if not os.path.exists(newDest): 
                                print('Copying file ' + row['from'] + ' to ' + newDest)
                                try: 
                                    zipfile.ZipFile(newDest, mode='w').write(row['from'])
                                except:
                                    print('Failed to copy file ' + row['from'] + ' to ' + newDest)
                            else: 
                                print('File already exists! Skipping ... ')
                        except: 
                            print('Failed to copy file ' + row['from'] + ' to ' + newDest)
                    else: 
                        newDest = self.destination + crtDate + '/' + row['from'].split('/')[-1]
                        try: 
                            print('Copying ',row['from'],' to ',newDest)
                            shutil.copy(row['from'], newDest)
                        except: 
                            print('Failed to copy file ' + row['from'] + ' to ' + newDest)
                
                else: 
                    if row.compression == 'zip': 
                        newDest = os.path.join(*[self.destination, crtDate , row.newName.split('.')[0] + '.zip'])

                        try:
                            os.makedirs(os.path.join('/', *newDest.split('/')[:-1]), exist_ok=True)

                            if not os.path.exists(newDest): 
                                print('Copying file ' + row['from'] + ' to ' + newDest)
                                zipfile.ZipFile(newDest, mode='w').write(row['from'])
                            else: 
                                print('File already exists! Skipping ... ')
                        except: 
                            print('Failed to copy file ' + row['from'] + ' to ' + newDest)
                    else: 
                        newDest = self.destination + crtDate + '/' + row.newName

                        try:
                            os.makedirs(os.path.join('/', *newDest.split('/')[:-1]), exist_ok=True)
                            if not os.path.exists(newDest): 
                                print('Copying file ' + row['from'] + ' to ' + newDest)
                                shutil.copy(row['from'], newDest)
                            else: 
                                print('File already exists! Skipping ... ')
                        except: 
                            print('Failed to copy file ' + row['from'] + ' to ' + newDest)

    def convertBytesToMb(self, bytesValue):
        return (bytesValue / 1000000.0) / 1024.0

    def getNecessarySpace(self, row):
        if os.path.exists(row['from']): 
            if os.path.isdir(row['from']):
            
                total_size = 0

                for dirpath, dirnames, filenames in os.walk(row['from']):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        total_size += os.path.getsize(fp)

                row['necessarySpaceInGB'] = self.convertBytesToMb(total_size)
                return row 
            else: 
                row['necessarySpaceInGB'] = self.convertBytesToMb(os.path.getsize(row['from']))
                return row 
        else:
            print('path does not exist ')
            row['necessarySpaceInGB'] = 0 
            return row 

    def getAvailableSpace(self, pth):
        return self.convertBytesToMb(os.statvfs(pth).f_frsize * os.statvfs(pth).f_bavail)

class Mail:
    def __init__(self, subject: str, body: str):
        self.subject = subject 
        self.body = body

    def send(self):
        print('If e-mail client is configured. This would send an alert e-mail ...')

####################################################################################################
# DEFINING FUNCTIONS
####################################################################################################
def sep():
    if sys.platform.startswith('linux'):
        return '/'
    if sys.platform.startswith('win'):
        return '\\'

def getProgParams(arg, parName):
    # function to check if env var are defined if not take from command line
    # env variables have priority
    if os.getenv(parName) is None:
        return arg
    else:
        return arg

def getExecutablePath():
    """
    :param arg: no argument required
    :return: returns the path to the executable file used in the script
    """
    pathToFile = sys.argv[0]
    pathToFile = pathToFile[1 +
                            len(os.path.commonprefix([os.getcwd(), pathToFile])):]
    return os.getcwd() + sep() + pathToFile

def getCmdLineArguments():
    # function to create a dictionary of arguments passed from the cmdline
    dictVal = {}  # Creating an empty dictionary
    argv = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argv, "hd:f:t:c:", [
                                   "SYNCHDD_DAYS_KEEP=", "SYNCHDD_INSTRUCTION_FILE=", "SYNCHDD_TARGET=", "SYNCHDD_ADD_TO_CRON="])
    except getopt.GetoptError:
        print('getCmdLineArguments: Failed to get command line arguments ...')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(
                "\nHelp Message:\nsyncHDD.py --SYNCHDD_DAYS_KEEP [integer] --SYNCHDD_FROM [path] --SYNCHDD_TO [path] --SYNCHDD_LOG [path]\n")
            sys.exit()
        elif opt in ("-t", "--SYNCHDD_TARGET"):
            dictVal['SYNCHDD_TARGET'] = getProgParams(arg, 'SYNCHDD_TARGET')
        elif opt in ("-d", "--SYNCHDD_DAYS_KEEP"):
            dictVal['SYNCHDD_DAYS_KEEP'] = getProgParams(arg, 'SYNCHDD_DAYS_KEEP')
        elif opt in ("-d", "--SYNCHDD_ADD_TO_CRON"):
            dictVal['SYNCHDD_ADD_TO_CRON'] = getProgParams(arg, 'SYNCHDD_ADD_TO_CRON')    
        elif opt in ("-f", "--SYNCHDD_INSTRUCTION_FILE"):
            dictVal['SYNCHDD_INSTRUCTION_FILE'] = getProgParams(arg, 'SYNCHDD_INSTRUCTION_FILE')
        elif opt in ("-v", "--verbose"):
            prm = getProgParams(arg, 'verbose')
            prm = '0' if ('' == prm) else prm
            dictVal['VERBOSE'] = int(prm)

    execLine = ''

    shapeExecLine = Switcher()

    for prm in list(dictVal.keys()):
         execLine = execLine + shapeExecLine.getMethod(prm, dictVal)
    dictVal['execLine'] = ' '.join(
        [sys.executable, getExecutablePath(), execLine])
    
    return dictVal

def main():
    dictVal = getCmdLineArguments()

    timeCheck = timeTheScript()
    disk = Disk(dictVal)

    if (disk.checkHDDConnected() and not disk.todayExists()):
        try:
            disk.removeOldDays()

            tf = processTransfer(dictVal)
            tf.run()

            mail = Mail('Files have been copied to HDD', '\n\nThe files have been automatically copied to external HDD.\n\n')
            mail.send()
        except:
            print("HDD is connected but function failed to execute")

    if dictVal['SYNCHDD_ADD_TO_CRON']:
        cmd = sys.executable + ' -u ' +  os.path.abspath(__file__) + ' --SYNCHDD_DAYS_KEEP ' + dictVal['SYNCHDD_DAYS_KEEP'] + ' --SYNCHDD_INSTRUCTION_FILE ' + dictVal['SYNCHDD_INSTRUCTION_FILE'] + ' --SYNCHDD_TARGET ' + dictVal['SYNCHDD_TARGET'] + ' --SYNCHDD_ADD_TO_CRON False ' + ' >> /tmp/SYNCHDD_script.log 2>&1 &'

        print('Following line will be added to cron: ' + cmd)
        
        cron = CronTab(user = os.getlogin())
        isJob = list(cron.find_command(cmd))
        if not isJob:
            print('Adding job to cron ...')
            job = cron.new(command=cmd)
            job.every_reboot()
            cron.write()
        else:
            print('Job already exists ...')
    
    print('Script took: ' + str(timeCheck.showTimeSpent()))
####################################################################################################
# MAIN
####################################################################################################
if __name__ == "__main__":
    while True:
        main()
        time.sleep(60)
        