#################################################################
# The imaging script is designed for the joint JIC and TGAC     #
# Wheat Growth research project and CropQuant device.           #
#                                                               #
#    Author: Dr Ji Zhou, ji.zhou@tgac.ac.uk; ji.zhou@jic.ac.uk  #
#    Date: 1st November 2015, V0.1 10th May 2015                #
#    Version: 1.1 on TGAC internal Github                       #
#    picamera version: 1.05                                     #
#    Software license: BSD license, the algorithm below is      #
#    developed by Dr Zhou and his team, which shall only be     #
#    used for the TGAC/JIC Wheat Programme.                     #
#                                                               #
#    Changes: 1) Add result folder                              #
#             2) Change the time stamp                          #
#             3) Rectify USB memory pen issue                   #
#             4) Add file size detection                        #
#             5) Remove simpleCV to reduce complexity           #
#                                                               #
#################################################################

import time
import os
from shutil import move
from utilities import Utilities
from imaging.camera import Camera


class ImageCapture(object):

    instance = None

    @staticmethod
    def getInstance():
        if ImageCapture.instance is None:
            ImageCapture.instance = ImageCapture()
        return ImageCapture.instance

    def __init__(self):
        super(ImageCapture, self).__init__()


    def initExperimentSettings(self):
        if 'capture' not in Utilities.getConfig():
            self.experiment = ''
            self.deviceid = ''
            self.replicate = ''
            self.duration = ''
            self.endtime = ''
            self.imageid = 0
            return

        config = Utilities.getConfig()['capture']

        try:
            self.experiment = config['experiment']
        except:
            self.experiment = ''

        try:
            self.deviceid = config['deviceid']
        except:
            self.deviceid = ''

        try:
            self.replicate = config['replicate']
        except:
            self.replicate = ''

        try:
            self.duration = config['duration']
        except:
            self.duration = ''

        try:
            self.endtime = config['endtime']
        except:
            self.endtime = ''

        if 'imageid' in config:
            self.imageid = config['imageid']
        else:
            self.imageid = 0

    def checkFinished(self):

        if self.endtime == '':
            return

        if time.time() > self.endtime:
            print('defined experiment finished')
            Utilities.getConfig().pop('capture', None)
            Utilities.saveConfig()

        else:

            Utilities.getConfig()['capture']['imageid'] = (int(self.imageid)+1)
            Utilities.saveConfig()


    def capture(self, saveAll=False):

        self.initExperimentSettings()

        # -- Getting the date and time
        # Time and date need to be set up on rapsberry pi first!
        timestamp = Utilities.get_date_time()
        curYear = timestamp[0]
        curMonth = timestamp[1]
        curDay = timestamp[2]
        curHour = timestamp[3]
        curMin = timestamp[4]

        print("Experiment name: %s\nImaging device: %s\nBiological replicates: %s\n Days: %s" % (
            self.experiment, self.deviceid, self.replicate, self.duration))
        # print curDay, curMonth, curYear
        CurrentDir = os.getcwd()

        ResultFolder = 'Experiment_%d' % curDay + '-%d' % curMonth + '-%d' % curYear

        expFolderName = self.experiment
        if expFolderName == '':
            expFolderName = 'Unnamed_CropQuant_Experiment'

        # If usb card has been inserted

        medialist = []
        superfolder = ''
        #
        # if os.path.exists("/media/pi"):
        #     medialist = os.listdir("/media/pi")
        #     superfolder = '/pi/'
        # else:
        #     medialist = os.listdir("/media")
        #
        # if len(medialist) > 0:
        #     ResultDirectory_BackUp = '/media/' + superfolder + medialist[0] + '/' + expFolderName
        #     ResultDirectory_IMG = '/home/pi/Desktop/' + expFolderName
        # else:
        #     #Utilities.ledblink(1)
        #     ResultDirectory_BackUp = '/cropquant/Backup/' + expFolderName
        #     # The USB has not been inserted
        #     ResultDirectory_IMG =   '/home/pi/Desktop/' + expFolderName

        ResultDirectory_BackUp = '/mnt/usb/' + expFolderName
        ResultDirectory_IMG = '/home/pi/Desktop/' + expFolderName


        if not os.path.exists(ResultDirectory_BackUp):
            os.makedirs(ResultDirectory_BackUp)

        if not os.path.exists(ResultDirectory_IMG):
            os.makedirs(ResultDirectory_IMG)

        # Finish creating the result folder

        # for i in range(int(self.duration) * 24 * 3):  # set how many shots to take in the field
        # In order not to exceed the memory limit
        # The data will be backed up in a usb memory E2pen

        # Establish a day folder that contains all images captured in a particular day
        # In DD_MM_YY
        #DayResultFolder = 'Date_%d' % curDay + '_%d' % curMonth + '_%s' % str(curYear)[-2:]
        DayResultFolder = 'Date_%s' % str(curYear)[-2:] + '_%d' % curMonth + '_%d' % curDay
        DayResultDirectory_BackUp = ResultDirectory_BackUp + '/' + DayResultFolder
        DayResultDirectory_IMG = ResultDirectory_IMG + '/' + DayResultFolder
        # DayResultDirectory_Bad = DayResultDirectory_BackUp + '/Discarded'

        # Detect whether or not the day folder has been created
        if not os.path.exists(DayResultDirectory_BackUp):
            os.makedirs(DayResultDirectory_BackUp)
        # if not os.path.exists(DayResultDirectory_Bad): # Bad image folder
        #    os.makedirs(DayResultDirectory_Bad)
        if not os.path.exists(DayResultDirectory_IMG):
            os.makedirs(DayResultDirectory_IMG)
        # Create the day folder to store captured images

        # Set up image name
        # Read teh imaging date/time
        timestamp = Utilities.get_date_time()
        curYear = timestamp[0]
        curMonth = timestamp[1]
        curDay = timestamp[2]
        curHour = timestamp[3]
        curMin = timestamp[4]
        # Form the image filename
        filename = self.experiment + '_Rep%s' % self.replicate + '_%s' % self.deviceid + '_ID-%02d' % (
        self.imageid + 1) + '_Date-%d' % curYear + '-%d' % curMonth + '-%d' % curDay + '_%d' % curHour + '-%d' % curMin + '.jpg'
        # Taking an image

        capturedfiles = Camera.getInstance().capture(filename)

        # Print out how many has been imaged

        modifier = 'th'
        indexmodulus = self.imageid % 10

        if indexmodulus == 0 and self.imageid != 10:
            modifier = 'st'
        elif indexmodulus == 1 and self.imageid != 11:
            modifier = 'nd'
        elif indexmodulus == 2 and self.imageid != 12:
            modifier = 'rd'

        print('The %d' % (self.imageid + 1) + '%s run: ' % modifier + 'Captured image %s' % filename)

        for file in capturedfiles:

            # Test the size of the file, remove SimpleCV
            # img = img.edges()
            file_stat = os.stat(file)
            filesize = 1.0 * file_stat.st_size / (1024 ** 2)
            print ('Image size: ' + str(round(filesize, 3)) + 'MB')

            #if filesize >= 3.0:  # file has a normal image size, 3.0MB
            if filesize >= 1.0 or saveAll:  # file has a normal image size, 3.0MB
                # Organise the image path for file transfer
                imagePath = CurrentDir + '/'
                Utilities.fileTransfer(imagePath, DayResultDirectory_BackUp, file)

                # Move the captured image file to the result folder
                move(CurrentDir + '/' + file, DayResultDirectory_IMG + '/' + file)

            else:
                # Organise the image path for file transfer
                imagePath = CurrentDir + '/'
                # fileTransfer(imagePath, DayResultDirectory_Bad, filename)
                # Delete the bad image file
                os.remove(file)
            # camera.stop_preview()

        self.checkFinished()
        # Finish powering the camera

