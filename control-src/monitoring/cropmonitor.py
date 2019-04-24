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

from datatransmit import HTTPTransmit
from pistatus import PiStatus
from sensorlog import SensorLog
from utilities import Utilities
from imaging.snapshot import Snapshot
from imaging.imagebackup import ImageBackup
import os
import json
import time
import subprocess
from shutil import copyfile

class CropMonitor:


    host = Utilities.get_server_ip()

    uploader = 'flask'

    #@staticmethod
    #def captureStatus():
     #   SensorLog.log()

    @staticmethod
    def transmitStatus(sensorprobe=True):
        pingFrequency = int(Utilities.getArgmap()['status'])
        hostfile = 'datainput.php'

        #SensorLog.log()

        transmitter = HTTPTransmit(CropMonitor.host + "/" + hostfile, 'RywyD7WHf2cSp7REqzkHyNEy', 'MQV3HKs5VkBTDFCpHEc7aYxP')
        if transmitter.available():

            data = PiStatus.getPiStatus(sensorprobe=sensorprobe)
            data['duration'] = pingFrequency
            CropMonitor.logStatus(data)
            retCode = transmitter.transmit(data)
            print("transmitted status with return code " + str(retCode))

        else:

            data = PiStatus.getPiStatus(sensorprobe=sensorprobe)
            data['duration'] = pingFrequency
            CropMonitor.logStatus(data)
            print("Transmission target not available (" + transmitter.target + ")")



    @staticmethod
    def imageUpload():
        hostfile = 'snapshotupload.php'

        transmitter = HTTPTransmit(CropMonitor.host + "/" + hostfile, 'RywyD7WHf2cSp7REqzkHyNEy', 'MQV3HKs5VkBTDFCpHEc7aYxP')
        if transmitter.available():
            img = Snapshot()

            if img.available():
                print('Uploading image: ' + img.getImage())
                scaledimage = img.getScaledImage()
                copyfile(scaledimage, "/opt/cropquant/interface/static/latest.jpg")
                print('Transmitting: ' + scaledimage + ' ' + img.getName())
                transmitter.upload(scaledimage, img.getName())
                img.clean()
            else:
                print('Failed to upload image')
        else:
            print("Transmission target not available (" + transmitter.target + ")")

    @staticmethod
    def imageBackup():
        hostfile = 'imageupload.php'

        print('making transmitter')

        if CropMonitor.uploader == 'php':

            transmitter = HTTPTransmit(CropMonitor.host + "/" + hostfile, 'RywyD7WHf2cSp7REqzkHyNEy',
                                       'MQV3HKs5VkBTDFCpHEc7aYxP')
        else:
            transmitter = HTTPTransmit(CropMonitor.host + ":8082/RywyD7WHf2cSp7REqzkHyNEy/MQV3HKs5VkBTDFCpHEc7aYxP")

        print('checking availability')
        if transmitter.available():
            print('Images:')
            images = ImageBackup.getImageList()

            for img in images:
                print(img)

            for img in images:

                try:
                    print('Uploading image: ' + img['name'])
                    transmitter.upload(img['filepath'], img['name'])
                except Exception as e:
                    print('Failed to upload image')
                    print(e)
        else:
            print("Transmission target not available (" + transmitter.target + ")")

    @staticmethod
    def logStatus(data):

        sensorlog = {}
        sensorlog['logs'] = []

        if os.path.exists(Utilities.getConfigFolderItem('sensorlog.json')):
            with open(Utilities.getConfigFolderItem('sensorlog.json'), 'r') as logFile:
                sensorlog = json.loads(logFile.read())

        log = {'timestamp': time.time()}
        log['data'] = data

        sensorlog['logs'].append(log)

        if os.path.exists(Utilities.getConfigFolderItem('sensorlog.json')):
            os.remove(Utilities.getConfigFolderItem('sensorlog.json'))

        with open(Utilities.getConfigFolderItem('sensorlog.json'), 'w') as logFile:
            logFile.write(json.dumps(sensorlog))

    @staticmethod
    def logToSystemCSV(line):


        csvFile = Utilities.getConfigFolderItem('systemlog.csv')

        if not os.path.exists(csvFile):
            with open(csvFile, 'w') as f:
                f.write(
                    'Datetime,CPU Temperature (C),CPU Usage (%),RAM Usage (%')

        with open(csvFile, 'a') as f:
            f.write(line)

        if os.path.exists('/home/pi'):
            if os.path.exists('/home/pi/Desktop'):
                if os.path.exists('/home/pi/Desktop/systemlog.csv'):
                    os.remove('/home/pi/Desktop/systemlog.csv')
                try:
                    subprocess.call("cp " + csvFile + " /home/pi/Desktop/systemlog.csv", shell=True)
                    subprocess.call("chmod 666 /home/pi/Desktop/systemlog.csv", shell=True)
                except:
                    print("Failed to copy CSV file")

    @staticmethod
    def logToSensorCSV(line):

        csvFile = Utilities.getConfigFolderItem('sensorlog.csv')

        if not os.path.exists(csvFile):
            with open(csvFile, 'w') as f:
                f.write(
                    'Datetime,Temperature (C),Relative Humidity (%),Light Levels (%),Soil Temperature (C),Soil Humidity (%)')

        with open(csvFile, 'a') as f:
            f.write(line)

        if os.path.exists('/home/pi'):
            if os.path.exists('/home/pi/Desktop'):
                if os.path.exists('/home/pi/Desktop/sensorlog.csv'):
                    os.remove('/home/pi/Desktop/sensorlog.csv')
                try:
                    subprocess.call("cp " + csvFile + " /home/pi/Desktop/sensorlog.csv", shell=True)
                    subprocess.call("chmod 666 /home/pi/Desktop/sensorlog.csv", shell=True)
                except:
                    print("Failed to copy CSV file")

