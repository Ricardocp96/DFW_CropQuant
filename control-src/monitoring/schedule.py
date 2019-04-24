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

from scheduling.scheduler import Scheduler

class MonitorSchedule:

    @staticmethod
    def schedule():

        if not Scheduler.isPresent('status'):
            Scheduler.add('03,33 * * * *', '-status 30')

        if not Scheduler.isPresent('imageupload'):
            Scheduler.add('01 01 * * *', '-imageupload')

        if not Scheduler.isPresent('capture'):
            Scheduler.add('01 01 * * *', '-imageupload')
