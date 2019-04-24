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
import subprocess
import time
from utilities import Utilities
import random
import netifaces

class Scheduler:
    shedulefile = '/etc/crontab'

    @staticmethod
    def isPresent(command):
        try:
            with open(Scheduler.shedulefile, 'r') as file:
                for line in file.readlines():
                    if 'cropquant -' + command in line:
                        return True
            return False
        except:
            return False

    @staticmethod
    def remove(command):
        lines = []

        try:
            with open(Scheduler.shedulefile, 'r') as file:
                lines = file.readlines()

            with open(Scheduler.shedulefile, 'w') as file:
                for line in lines:
                    if 'cropquant -' + command not in line:
                        file.write(line)
        except:
            return False


    @staticmethod
    def add(schedule, arguments, user='root'):
        try:
            with open(Scheduler.shedulefile, 'a') as file:
                file.write(schedule + " " + user + " /usr/local/bin/cropquant " + arguments + "\n")
                print('adding: ' + schedule + " " + user + " /usr/local/bin/cropquant " + arguments)
        except:
            return False

    @staticmethod
    def shedule():

        print('Scheduling CropQuant Services')

        offset = 0

        try:
            ipend = netifaces.ifaddresses('bat0')[netifaces.AF_INET][0]['addr'].split('.')[-1]
            offset = int(ipend)
        except:
            offset = random.randint(0, 255)


        config = Utilities.getConfig()

        print("Config:")
        print(config)

        # Scheduling image backup
        backup_offset = offset % 16

        backuphour = 0
        backupminute = backup_offset*15

        while backupminute >= 60:
            backuphour += 1
            backupminute -= 60

        backupshedule = str(backupminute) + ' ' + str(backuphour) + ' * * *'
        Scheduler.remove("imagebackup")
        Scheduler.add(backupshedule, "-imagebackup")

        if 'schedule' not in config:
            return

        # Scheduling Image Capture
        if 'image' in config['schedule']:
            try:
                if config['schedule']['image'] == 0:
                    Scheduler.remove("capture")
                else:
                    interval = 60/int(config['schedule']['image'])
                    imagemins = [0]

                    for i in range(1, int(config['schedule']['image'])):
                        imagemins.append(i*interval)

                    for i in range(0, len(imagemins)):
                        imagemins[i] += offset
                        while imagemins[i] >= 60:
                            imagemins[i] -= 60

                    imagetime = ""
                    for t in imagemins:
                        if imagetime != "":
                            imagetime = imagetime + ","
                        imagetime = imagetime + str(t)

                    imagetime = imagetime + " * * * *"

                    Scheduler.remove("capture")
                    Scheduler.add(imagetime, "-capture")

            except Exception as e:
                print e

        # Scheduling Sensor Capture
        if 'sensor' in config['schedule']:
            try:
                interval = 60 / int(config['schedule']['sensor'])
                monitorminsmins = [0]

                for i in range(1, int(config['schedule']['sensor'])):
                    monitorminsmins.append(i * interval)

                for i in range(0, len(monitorminsmins)):
                    monitorminsmins[i] += offset
                    while monitorminsmins[i] >= 60:
                        monitorminsmins[i] -= 60

                monitortime = ""
                for t in monitorminsmins:
                    if monitortime != "":
                        monitortime = monitortime + ","
                    monitortime = monitortime + str(t)

                monitortime = monitortime + " * * * *"

                Scheduler.remove("status")
                Scheduler.add(monitortime, "-status 30")

            except Exception as e:
                print e

        # Scheduling Overview
        if 'overview' in config['schedule']:
            try:
                Scheduler.remove("overviewcapture")
                for timepoint in config['schedule']['overview']:
                    parts = timepoint.split(':')
                    overviewtime = parts[1] + " " + parts[0] + " * * *"
                    Scheduler.add(overviewtime, "-overviewcapture")
            except Exception as e:
                print e

        snapshottime = str(random.randint(0,59)) + " 01 * * *"
        Scheduler.remove("imageupload")
        Scheduler.add(snapshottime, "-imageupload")
