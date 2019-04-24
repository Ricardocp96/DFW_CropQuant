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

#### DEPENDENCIES ####

# python-netifaces
# python-psutils
# python-flask
# python-pillow
# python-requests


from utilities import Utilities
from imaging.capture import ImageCapture
from imaging.camera import Camera
from imaging.focustest import FocusTest
from interface.web import WebInterface
from monitoring.cropmonitor import CropMonitor
from scheduling.scheduler import Scheduler
import os
import RPi.GPIO as GPIO
from sensors.combinedsensor import CombinedSensor
from reset import FactoryReset

import traceback

Camera.setCameraMode(Camera.CAMERA_PI)

# netifaces
# psutil
# onvif

########################### SCHEDULED TASKS ################################

def stopWebcam():
    try:
        os.system("sudo service motion stop")
    except:
        i=0
stopWebcam()


try:

    if 'reset' in Utilities.getArgmap():
        FactoryReset.reset()
        exit(0)

    if 'capture' in Utilities.getArgmap():
        try:
            Utilities.getServerTime()
        except Exception as e:
            print(e)
        imagecapture = ImageCapture()
        imagecapture.capture(saveAll=True)
        exit(0)

    if 'status' in Utilities.getArgmap():
        CropMonitor.transmitStatus(sensorprobe=False)
        exit(0)

    if 'imageupload' in Utilities.getArgmap():
        CropMonitor.imageUpload()
        exit(0)

    if 'imagebackup' in Utilities.getArgmap():
        CropMonitor.imageBackup()
        exit(0)

    if 'focustest' in Utilities.getArgmap():
        FocusTest.Run()
        exit(0)

    if 'time' in Utilities.getArgmap():
        try:
            Utilities.getServerTime()
        except Exception as e:
            print("Failed to get server time")
            print(e)
        exit(0)

    if 'sensortest' in Utilities.getArgmap():
        try:
            CombinedSensor.getInstance().test()
        except Exception as e:
            print(e)
        exit(0)
except Exception as e:
    print(e)

    traceback.print_exc()
    exit(1)

Scheduler.shedule()

########################### INTERFACE ################################

modules = []


interface = WebInterface(modules)

try:
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(5, GPIO.OUT, initial=1)
except Exception as e:
    print(e)

interface.start()