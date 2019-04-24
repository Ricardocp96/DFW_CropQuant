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
import PIL
from PIL import Image

class Snapshot:

    def __init__(self):

        print('Finding Image')

        targetfolder = self.foldername()

        found = False
        dayfolder = ''
        for root, dirs, files in os.walk("/mnt/usb", topdown=False):
            if not found:
                for name in dirs:
                    if not found:
                        if targetfolder in name:
                            found = True
                            dayfolder = os.path.join(root, name)

        if not found:
            print('Could not find yesterdays image folder')
            self.image = ''

            imagesize = -1
            datename = self.standalonefilename()
            self.imagescaled = ''

            for root, dirs, files in os.walk("/mnt/usb", topdown=False):
                for name in files:
                    if 'jpg' in name and datename in name:
                        s = os.path.getsize(os.path.join(root, name))
                        if s > imagesize:
                            imagesize = s
                            self.image = os.path.join(root, name)

            return

        imagefiles  = []

        for img in os.listdir(dayfolder):
            imgfile = os.path.join(dayfolder, img)
            if os.path.isfile(imgfile):
                s = os.path.getsize(imgfile)
                if s > 0:
                    imagefiles.append([s, imgfile])

        def getKey(item):
            return item[0]

        imagefiles = sorted(imagefiles, key=getKey)

        index = int(len(imagefiles) * 0.9)



        if index < 0:
            print('Could not find suitable image')
            self.image = ''
            return

        self.image = imagefiles[index][1]

        print('Found: ' + imagefiles[index][1])

        self.imagescaled = ''

        print('Done')

    def setImage(self, filename):
        self.image = filename
        self.imagescaled = ''

    def getName(self):
        head, tail = os.path.split(self.image)
        return tail

    def scale(self):
        print('Scaling Image')
        basewidth = 480
        img = Image.open(self.image)
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))

        self.imagescaled = './scaledimage.jpg'
        img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
        img.save(self.imagescaled)

        print('Done')

        return


    def available(self):
        if self.image != '':
            return True
        return False

    def getImage(self):
        return self.image

    def getScaledImage(self):
        self.scale()
        return self.imagescaled

    def clean(self):
        print('Cleaning')
        if os.path.exists(self.imagescaled) and self.imagescaled != '':
            os.remove(self.imagescaled)
        print('Done')

    def foldername(self):
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime('Date_%y_%-m_%-d')

    def standalonefilename(self):
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime('%Y-%m-%d')