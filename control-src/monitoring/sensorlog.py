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

from utilities import Utilities
import subprocess
import time
import psutil
import struct
from smbus import SMBus
from sensors.combinedsensor import CombinedSensor
from sensors.ambientsensor import AmbientSensor

class SensorLog():

    @staticmethod
    def log(sensorprobe=True):

        if sensorprobe:
            if CombinedSensor.getInstance().available():
                data = CombinedSensor.getInstance().read()
            else:
                data = {}
        else:
            data = {}

        try:
            data['cputemp'] = SensorLog.getCPUTemp()
        except:
            data['cputemp'] = ''

        try:
            data['cpuuse'] = psutil.cpu_percent(interval=1)
        except:
            data['cpuuse'] = ''

        try:
            data['memuse'] = psutil.virtual_memory().percent
        except:
            data['memuse'] = ''

        return data

    @staticmethod
    def getCPUTemp():

        try:
            output = subprocess.check_output("vcgencmd measure_temp", shell=True).strip().split('\n')

            for line in output:
                if 'temp=' in line:
                    if "'" in line:
                        return line.split('=')[1].split("'")[0]
            return ''
        except:
            print('Unable to find CPU temp')
            return ''