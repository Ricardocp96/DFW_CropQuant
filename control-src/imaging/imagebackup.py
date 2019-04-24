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

from datetime import datetime, timedelta
import os

class ImageBackup:

    @staticmethod
    def getImageList():

        targetfolder = ImageBackup.foldername()
        print(targetfolder)
        found = False
        dayfolder = ''
        for root, dirs, files in os.walk("/mnt", topdown=False):
            if not found:
                for name in dirs:
                    if not found:
                        if targetfolder in name:
                            found = True
                            dayfolder = os.path.join(root, name)

        if not found:
            print('Could not find yesterdays image folder')
            return []

        imagefiles = os.listdir(dayfolder)

        yesterdays_images = []

        for file in imagefiles:
            if '.jpg' in file:

                image = {}

                image['name'] = file
                image['filepath'] = os.path.join(dayfolder, file)

                yesterdays_images.append(image)

        return yesterdays_images

    @staticmethod
    def foldername():
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime('Date_%y_%-m_%-d')
