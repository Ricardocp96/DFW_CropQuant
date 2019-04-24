##############################################################################
#                                                                            #
# Copyright (C) The Zhou Laboratory - All Rights Reserved                    #
#                                                                            #
# This file is part of the CropQuant project                                 #
#                                                                            #
# Unauthorized copying of this file, via any medium is strictly prohibited   #
# Proprietary and confidential                                               #
# Written by Dr Daniel Reynolds <daniel.reynolds@earlham.ac.uk>              #
#                                                                            #
##############################################################################

import os
import json
import sys
import time
from shutil import copyfile
import socket
import subprocess
import struct
import requests

class Utilities:

    configfile = 'cropquant.json'
    configfolder = '/cropquant'
    loadtime = -1
    configdata = {}

    lockfilename = "lockfile.lck"
    haslock = False

    @staticmethod
    def lockfile():
        return os.path.join(Utilities.getConfigFolder(), Utilities.lockfilename)

    @staticmethod
    def getLockFile(task):

        start_time = time.time()

        while os.path.exists(Utilities.lockfile()):
            time.sleep(1)

            if (time.time() - start_time) >= (60*5):
                os.remove(Utilities.lockfile())


        open(Utilities.lockfile(), 'a').close()
        print("Lockfile created by " + task)
        Utilities.haslock = True

    @staticmethod
    def releaseLockFile(task):
        if Utilities.haslock:
            Utilities.haslock = False

        if os.path.exists(Utilities.lockfile()):
            os.remove(Utilities.lockfile())
        print("Lockfile released by " + task)

    @staticmethod
    def clearLockFile():
        Utilities.haslock = False
        if os.path.exists(Utilities.lockfile()):
            os.remove(Utilities.lockfile())


    @staticmethod
    def ledblink(a, b, c):
        try:
            os.system("cq_led " + str(a) + " " + str(b) + " " + str(c) + " &")
        except:
            return

    @staticmethod
    def getIDs():
        return

    @staticmethod
    def getConfig():

        if not os.path.exists(Utilities.getConfigFolderItem(Utilities.configfile)):
            print("no file")
            with open(Utilities.getConfigFolderItem(Utilities.configfile), 'w') as file:
                file.write("{}")

        modfied = os.path.getmtime(Utilities.getConfigFolderItem(Utilities.configfile))

        if modfied > Utilities.loadtime:
            print("modified")
            Utilities.loadtime = modfied
            with open(Utilities.getConfigFolderItem(Utilities.configfile), 'r') as file:
                Utilities.configdata = json.loads(file.read())

        return Utilities.configdata

    @staticmethod
    def saveConfig():

        if os.path.exists(Utilities.getConfigFolderItem(Utilities.configfile)):
            os.remove(Utilities.getConfigFolderItem(Utilities.configfile))

        with open(Utilities.getConfigFolderItem(Utilities.configfile), 'w') as file:
            file.write(json.dumps(Utilities.configdata))

    @staticmethod
    def setConfig(config):
        Utilities.configdata = config
        Utilities.saveConfig()

    arg_map = None

    @staticmethod
    def getConfigFolderItem(subfolder):

        return os.path.join(Utilities.getConfigFolder(), subfolder)

    @staticmethod
    def getMedian(list):
        test = list
        test.sort()
        index = len(test) // 2
        return test[index]

    @staticmethod
    def getConfigFolder():

        if not os.path.exists(Utilities.configfolder):
            subprocess.call("sudo mkdir " + Utilities.configfolder, shell=True)
            subprocess.call("sudo chmod -R 777 " + Utilities.configfolder, shell=True)

        return Utilities.configfolder

    @staticmethod
    def getSystemLogCSV():

        csvFile = Utilities.getConfigFolderItem('systemlog.csv')

        if not os.path.exists(csvFile):
            with open(csvFile, 'w') as f:
                f.write(
                    'Datetime,CPU Temperature (C),CPU Usage (%),RAM Usage (%)')

        return csvFile


    @staticmethod
    def logToSystemCSV(line):

        csvFile = Utilities.getSystemLogCSV()

        with open(csvFile, 'a') as f:
            f.write(line)

        if os.path.exists('/home/pi'):
            if os.path.exists('/home/pi/Desktop'):
                if os.path.exists('/home/pi/Desktop/systemlog.csv'):
                    os.remove('/home/pi/Desktop/systemlog.csv')
                try:
                    output = subprocess.check_output("cp " + csvFile + " /home/pi/Desktop/systemlog.csv", shell=True)
                    output = subprocess.check_output("chmod 666 /home/pi/Desktop/systemlog.csv", shell=True)
                except:
                    print("Failed to copy CSV file")

    @staticmethod
    def logToSensorCSV(line):
        csvFile = Utilities.getConfigFolderItem('sensorlog.csv')

        if not os.path.exists(csvFile):
            print("file non existing")
            with open(csvFile, 'w') as f:
                print("writing header")
                f.write(
                    'Datetime,Temperature (C),Relative Humidity (%),Light Levels (%)')

        with open(csvFile, 'a') as f:
            f.write(line)

        if os.path.exists('/home/pi'):
            if os.path.exists('/home/pi/Desktop'):
                if os.path.exists('/home/pi/Desktop/sensorlog.csv'):
                    os.remove('/home/pi/Desktop/sensorlog.csv')
                try:
                    output = subprocess.check_output("cp " + csvFile + " /home/pi/Desktop/sensorlog.csv", shell=True)
                    output = subprocess.check_output("chmod 666 /home/pi/Desktop/sensorlog.csv", shell=True)
                except:
                    print("Failed to copy CSV file")

    @staticmethod
    def getArgmap():

        if Utilities.arg_map is None:

            Utilities.arg_map = {}
            for i, argument in enumerate(sys.argv):
                if argument.startswith("-"):
                    if len(sys.argv) <= i + 1:
                        Utilities.arg_map[argument[1:]] = True
                    else:
                        if sys.argv[i + 1].startswith("-"):
                            Utilities.arg_map[argument[1:]] = True
                        else:
                            Utilities.arg_map[argument[1:]] = sys.argv[i + 1]

        return Utilities.arg_map

        #
        # Gets IP address of device to use for device ID0
        #

    @staticmethod
    def get_server_ip():

        ip = 'http://192.168.42.1'

        config = Utilities.getConfig()

        if 'server_ip' in config:
            ip = config['server_ip']

        return ip


    @staticmethod
    def get_ip_address(ifname):  # IP address based on socket information
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return socket.inet_ntoa(fcntl.ioctl(
            s.fileno(),
            0x8915,  # SIOCGIFADDR
            struct.pack('256s', ifname[:15])
        )[20:24])
        #return "10.0.0.0"

    #
    # Gets current date and time
    #
    @staticmethod
    def get_date_time():
        # Use raspberry pi time, local time, as the time point
        timestamp_local = time.localtime(time.time())
        return timestamp_local

    #
    #   Moves file
    #
    @staticmethod
    def fileTransfer(imagePath, resultPath, imagename):
        imageDir = imagePath + imagename
        resultDir = resultPath + '/' + imagename
        copyfile(imageDir, resultDir)

    @staticmethod
    def getSerial():
        # Extract serial from cpuinfo file
        cpuserial = "0000000000000000"
        try:
            f = open('/proc/cpuinfo', 'r')
            for line in f:
                if line[0:6] == 'Serial':
                    cpuserial = line[10:26]
            f.close()
        except:
            cpuserial = "ERROR000000000"

        return cpuserial

    @staticmethod
    def is_number(s):
        try:
            x = float(s)
            if s is 'NaN':
                return False
            else:
                if x > 0 and x < 0.0000001:
                    return False
                else:
                    return True
        except:
            return False


    @staticmethod
    def setUPSTimeout(secs=-1):
        try:
            if secs < 0:
                os.system("sudo i2cset -y 1 0x6B 9 0xff")
            else:
                os.system("sudo i2cset -y 1 0x6B 9 " + str(secs))
        except Exception as e:
            print(e)

    @staticmethod
    def getServerTime():
        try:
            r = requests.get(Utilities.get_server_ip() + "/timequery.php")
            os.system('sudo date -s "' + r.text + '"')
        except Exception as e:
            print(e)