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

import netifaces
import subprocess
from utilities import Utilities
import os
import datetime
from sensorlog import SensorLog
import time
import Adafruit_ADS1x15


class PiStatus:

    networkAddresses = {'macaddress': '', 'ipaddress': '', 'hostname': ''}

    def __init__(self):
        return

    # Compile node data and return
    @staticmethod
    def getPiStatus(sensorprobe=True):

        if sensorprobe:
            data = SensorLog.log(sensorprobe)
        else:
            data = {}


        data['storage'] = PiStatus.getStorage()
        data['uptime'] = PiStatus.getUptime()

        timestring = time.strftime("%d.%m.%Y - %H:%M:%S")

        if sensorprobe:
            Utilities.logToSystemCSV("\n" + timestring + "," + str(data['cputemp']) + "," + str(
                data['cpuuse']) + "," + str(data['memuse']))

        if 'temp' in data:
            if 'soiltemp' in data:
                Utilities.logToSensorCSV("\n" + timestring + "," + str(data['temp']) + "," + str(data['humid']) + "," + str(data['light']) + "," + str(data['soiltemp']) + "," + str(data['soilhumid']))
            else:
                Utilities.logToSensorCSV(
                    "\n" + timestring + "," + str(data['temp']) + "," + str(data['humid']) + "," + str(data['light']))

        data['kernel'] = PiStatus.getKernel()
        data['distro'] = PiStatus.getDistro()
        #data['version_cquant'] = PiStatus.getSoftwareVersion('cropquant')

        PiStatus.getNetworkAddress()


        try:
            data['projectid'] = Utilities.getConfig()['capture']['projectid']
        except Exception as e:
            print(e)

        data['macaddress'] = PiStatus.networkAddresses['macaddress']

        print(data['macaddress'])

        data['ipaddress'] = PiStatus.networkAddresses['ipaddress']
        data['hostname'] = PiStatus.networkAddresses['hostname']

        #data['cqid'] = Utilities.getSerial()

        data['latestimage'] = PiStatus.getLastImage()

        data['imagingstatus'] = int(PiStatus.isImagingRunning())

        data['position'] = PiStatus.getPosition()

        data['battery'] = PiStatus.get_battery_voltage()

        return data

    # Get system uptime
    @staticmethod
    def getUptime():

        nowsecs =  int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds())
        upsecs = 0
        with open('/proc/uptime', 'r') as uptime:
            upsecs = int(float(uptime.read().strip().split(' ')[0]))

        return nowsecs - upsecs

    @staticmethod
    def getPosition():
        if 'position' in Utilities.getConfig():
            return Utilities.getConfig()['position']
        else:
            return "0,0"


    @staticmethod
    def getKernel():
        try:
            output = subprocess.check_output("uname -r", shell=True)
            return output.strip().split('\n')[-1]
        except:
            print('Unable to find Distro')
            return ''

    @staticmethod
    def getSoftwareVersion(package):
        try:
            output = subprocess.check_output("dpkg -s " + package + " | grep Version", shell=True)
            line = output.strip().split('\n')[-1]
            return line.split(' ')[-1]
        except:
            print('Unable to find ' + package + ' version:')
            return ''

    @staticmethod
    def getDistro():
        try:
            output = subprocess.check_output("cat /etc/*-release | grep PRETTY", shell=True)
            line = output.strip().split('\n')[-1]
            return line.split('"')[-2]
        except:
            print('Unable to find Distro')
            return ''

    # Find all mounted storage devices and report space usage
    @staticmethod
    def getStorage():
        from os import listdir

        sizeList = []

        sizeList.append(PiStatus.queryPartitionSpace("/"))

        mountpoints = listdir("/mnt")

        for mountpoint in mountpoints:
            sizeList.append(PiStatus.queryPartitionSpace("/mnt/" + mountpoint))


        return sizeList

    # \get available/total space for a particular partition
    @staticmethod
    def queryPartitionSpace(partition):

        output = subprocess.check_output("df -BM " + "\"" + partition + "\"", shell=True)
        line = output.strip().split('\n')[-1]

        total = 0
        avail = 0

        lineIndex = -1
        for str in line.split(' '):
            if str != '':
                lineIndex = lineIndex + 1

                if lineIndex == 1:
                    total = str.replace('M', '')
                elif lineIndex == 3:
                    avail = str.replace('M', '')

        return {'mountpoint' : partition, 'total' : total, 'available' : avail}



    # Parse ifconfig to get network addresses
    @staticmethod
    def getNetworkAddress():

        networkInterface = 'eth0'

        for interface in netifaces.interfaces():
            if interface == 'wlan0':
                networkInterface = interface

        try:

            PiStatus.networkAddresses['macaddress'] = PiStatus.getMACAddress()
            PiStatus.networkAddresses['ipaddress'] = PiStatus.getIPAddress()

        except Exception as e:
            print(e)

        try:
            conf = Utilities.getConfig()['capture']
            PiStatus.networkAddresses['hostname'] = conf['deviceid']
        except:
            PiStatus.networkAddresses['hostname'] = Utilities.getSerial()

    @staticmethod
    def getStretchIPAddress():
        try:

            networkInterface = 'wlxec3dfde1196b'

            output = subprocess.check_output("ifconfig " + networkInterface, shell=True).strip().split('\n')

            ipaddress = ''

            for line in output:

                if 'inet ' in line:
                    parts = line.strip().split(' ')
                    next = False
                    for part in parts:

                        if next and part != '':
                            next = False
                            ipaddress = part.strip().split(' ')[0]

                        if 'inet' in part:
                            next = True

            return ipaddress

        except:
            return "127.0.0.1"

    @staticmethod
    def getIPAddress():

        try:

            networkInterface = 'wlan0'

            output = subprocess.check_output("ifconfig " + networkInterface, shell=True).strip().split('\n')

            ipaddress = ''

            for line in output:

                if 'inet addr' in line:
                    parts = line.strip().split(':')
                    next = False
                    for part in parts:

                        if next and part != '':
                            next = False
                            ipaddress = part.strip().split(' ')[0]

                        if 'inet addr' in part:
                            next = True

            return ipaddress

        except:
            return PiStatus.getStretchIPAddress()

    # parse ifconfig to get mac address without any other addresses
    @staticmethod
    def getMACAddress():

        macaddressstring = ''

        interface = ''

        for inter in os.listdir('/sys/class/net/'):
            if interface == '' or inter.startswith('wl'):
                interface = inter

        if interface == '':
            return

        address_file = os.path.join('/sys/class/net/', interface, 'address')

        try:
            with open(address_file) as file:
                macaddressstring = file.read().replace('\n','')
        except Exception as e:
            print(e)







        config = Utilities.getConfig()

        # networkInterface = 'eth0'
        #
        # for interface in netifaces.interfaces():
        #     if interface.startswith('wlx') or interface.startswith('wlan'):
        #         networkInterface = interface
        #
        # output = subprocess.check_output("ifconfig " + networkInterface, shell=True).strip().split('\n')
        #
        # macaddressstring = ''
        #
        # for line in output:
        #     if 'HWaddr' in line:
        #         parts = line.strip().split(' ')
        #         next = False
        #         for part in parts:
        #
        #             if next and part != '':
        #                 next = False
        #                 macaddressstring = part
        #
        #             if 'HWaddr' in part:
        #                 next = True



        if 'capture' in config:
            if 'projectid' in config['capture']:
                print(config['capture']['projectid'])
                macaddressstring = macaddressstring + config['capture']['projectid']
            else:
                print('no projectid')
        else:
            print('no capture')

        return macaddressstring

    @staticmethod
    def getLastImage():

        newestfile = ''
        newestdate = ''

        for root, dirs, files in os.walk('/mnt/usb'):
            for file in files:
                if file.endswith('.jpg'):
                    if newestfile == '':
                        newestfile = os.path.join(root, file)
                        newestdate = os.path.getctime(newestfile)
                    else:
                        if os.path.getctime(os.path.join(root, file)) > newestdate:
                            newestfile = os.path.join(root, file)
                            newestdate = os.path.getctime(newestfile)


        if newestfile == '':
            return 'No image found'

        return time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(newestdate))

    @staticmethod
    def isImagingRunning():

        found = False

        try:
            output = subprocess.check_output("ps -ef | grep WheatFieldTrial" , shell=True).strip().split('\n')

            for line in output:
                if 'python' in line:
                    found = True
        except:
            print('Failed to parse ps output')

        return found

    @staticmethod
    def get_battery_voltage():

        try:

            adc = Adafruit_ADS1x15.ADS1115()
            GAIN = 1

            recorded_values = []

            for i in range(5):
                try:
                    recorded_values.append(adc.read_adc(0, gain=GAIN))
                except Exception as e:
                    print(e)

            voltage = 0

            cum_voltage = 0

            for value in recorded_values:
                cum_voltage += value

            if len(recorded_values) > 0:
                voltage = cum_voltage / len(recorded_values)

            return str(voltage)

        except Exception as e:
            print(e)
            return '0'

