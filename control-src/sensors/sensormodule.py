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

from smbus import SMBus
import subprocess
from utilities import Utilities
import time
import struct

class SensorModule(object):

    def __init__(self):
        super(SensorModule, self).__init__()

    def available(self):

        try:

            output = subprocess.check_output("sudo i2cdetect -y 1", shell=True)

            for line in output:
                parts = line.split(':')
                if len(parts) > 1:
                    if str(hex(self.address)[2:]) in parts[-1]:
                        return True

        except Exception as e:
            print(e)
            return False
        return True

    @staticmethod
    def parsevalue(value, min, max):
        vstr = ''.join(chr(i) for i in value)
        x = struct.unpack('>f', vstr)[0]

        valid = True
        reading = 0

        if not Utilities.is_number(x):
            valid = False

        if x < min or x > max:
            valid = False

        if 'e' in vstr:
            valid = False

        if x > 0 and x < 0.00001:
            valid = False

        if valid:
            return x
        else:
            print('failing: ' + str(x))
            return None

    def test(self, buffersize):

        print("Sensor Test")

        bus = SMBus(1)

        bus.write_i2c_block_data(self.address, 0xAA, [0xAA])

        time.sleep(0.5)

        buffer = [0x01]
        while buffer[0] != 0x00:
            buffer = bus.read_i2c_block_data(self.address, 0, 1)
            time.sleep(0.1)
            Register = [buffer[0]]
            print(str(buffer[0]))
            i = 0

        for i in range(0,buffersize):
            buffer = bus.read_i2c_block_data(self.address, 0, 1)
            Register.append(buffer[0])
            print(str(buffer[0]))
            time.sleep(0.1)
