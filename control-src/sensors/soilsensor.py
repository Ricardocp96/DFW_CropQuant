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

class SoilSensor(SensorModule):

    instance = None

    @staticmethod
    def getInstance():
        if SoilSensor.instance is None:
            SoilSensor.instance = SoilSensor()
            if not SoilSensor.instance.available:
                SoilSensor.instance = None
        return SoilSensor.instance

    def __init__(self):
        super(SoilSensor, self).__init__()
        self.address = 0x73

    def read(self):
        raise NotImplementedError