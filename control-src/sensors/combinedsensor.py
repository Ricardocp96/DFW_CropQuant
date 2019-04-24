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

from sensors.sensormodule import SensorModule
from utilities import Utilities
import subprocess
import time
import struct
from smbus import SMBus
import traceback

class CombinedSensor(SensorModule):

    instance = None

    @staticmethod
    def getInstance():
        if CombinedSensor.instance is None:
            CombinedSensor.instance = CombinedSensor()
        return CombinedSensor.instance

    def __init__(self):
        super(CombinedSensor, self).__init__()
        #print (self.address)
        self.address = 0x29

    def test(self):
        super(CombinedSensor, self).test(25)

    def read(self):

        data = {}

        data['temp'] = 0
        data['humid'] = 0
        data['light'] = 0
        data['soiltemp'] = 0
        data['soilhumid'] = 0

        status = 1

        readings = [{},{},{}]



        for iteration in range(0,3):

            print('Iteration:' + str(iteration))

            tries = 3
            finished = False

            while tries > 0 and not finished:

                try:
                    success = True

                    print("Sensor probe - Try " + str(11 - tries))

                    bus = SMBus(1)

                    bus.write_i2c_block_data(self.address, 0xAA, [0xAA])

                    time.sleep(0.5)

                    buffer = [0x01]
                    while buffer[0] != 0x00:
                        buffer = bus.read_i2c_block_data(self.address, 0, 1)
                        time.sleep(0.1)
                        Register = [buffer[0]]
                        i = 0

                    while i < 25:
                        buffer = bus.read_i2c_block_data(self.address, 0, 1)
                        Register.append(buffer[0])
                        time.sleep(0.1)
                        i = i + 1



                    if 'temp' not in readings:
                        value = [Register[2], Register[3], Register[4], Register[5]]
                        val = SensorModule.parsevalue(value, -20, 100)

                        if val is not None:
                            readings[iteration]['temp'] = val
                        else:
                            print("Incorrect temp: " + str(val))
                            success = False



                    if 'humid' not in readings:
                        value = [Register[7], Register[8], Register[9], Register[10]]
                        val = SensorModule.parsevalue(value, 0, 100)

                        if val is not None:
                            readings[iteration]['humid'] = val
                        else:
                            print("Incorrect humid: " + str(val))
                            success = False


                    if 'light' not in readings:
                        value = [Register[12], Register[13], Register[14], Register[15]]
                        val = SensorModule.parsevalue(value, 0, 100)

                        if val is not None:
                            readings[iteration]['light'] = val
                        else:
                            print("Incorrect light: " + str(val))
                            success = False


                    if 'soilhumid' not in readings:
                        value = [Register[17], Register[18], Register[19], Register[20]]
                        val = SensorModule.parsevalue(value, 0, 100)

                        if val is not None:
                            readings[iteration]['soilhumid'] = val
                        else:
                            print("Incorrect soilhumid: " + str(val))
                            success = False


                    if 'soiltemp' not in readings:
                        value = [Register[22], Register[23], Register[24], Register[25]]
                        val = SensorModule.parsevalue(value, -20, 100)

                        if val is not None:
                            readings[iteration]['soiltemp'] = val
                        else:
                            print("Incorrect soiltemp: " + str(val))
                            success = False

                    if not success:
                        tries = tries - 1
                        time.sleep(1.0)
                    else:
                        finished = True

                except Exception as e:
                    print("Exception reading 12c device")
                    print(e)
                    traceback.print_exc()
                    tries = tries - 1
                    time.sleep(2.0)
                    subprocess.call("sudo i2cdetect -y 1", shell=True)


        print("Readings logged:")

        dataset = {}

        for set in readings:
            for key, value in set.iteritems():
                if key not in dataset:
                    dataset[key] = []
                dataset[key].append(value)

        if 'temp' not in dataset:
            dataset['temp'] = [0]
        if 'humid' not in dataset:
            dataset['humid'] = [0]
        if 'light' not in dataset:
            dataset['light'] = [0]
        if 'soiltemp' not in dataset:
            dataset['soiltemp'] = [0]
        if 'soilhumid' not in dataset:
            dataset['soilhumid'] = [0]



        for key, value in dataset.iteritems():
            data[key] = Utilities.getMedian(value)



        print(data)

        return data