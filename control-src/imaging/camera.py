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
import picamera
import os
from utilities import Utilities
# import requests
# from onvif import ONVIFCamera


#
# Camera Superclass
# Extended by camera implementations
#
class Camera(object):

    instance = None

    CAMERA_NETWORK = 3
    CAMERA_PI = 1
    CAMERA_USB = 2

    cameramode = CAMERA_PI

    @staticmethod
    def setCameraMode(mode):
        Camera.cameramode = mode
        Camera.instance = None

    @staticmethod
    def getInstance():
        if Camera.instance is None:
            if int(Camera.cameramode) == 3:
                Camera.instance = EthernetCamera()
            elif int(Camera.cameramode) == 2:
                Camera.instance = USBCamera()
            elif int(Camera.cameramode) == 1:
                Camera.instance = PiCamera()
        return Camera.instance

    def getCameraSettings(self):
        self.camera_settings = []
        return self.camera_settings

    def getCameraSetting(self, name):
        for setting in self.camera_settings:
            if setting['command'] == name:
                return setting
        return None

    def __init__(self):
        super(Camera, self).__init__()

#
# Capture by raspberry pi camera
#

class PiCamera(Camera):

    def __init__(self):
        super(PiCamera, self).__init__()

    def capture(self, filename):
        with picamera.PiCamera() as camera:

            # -- Camera setting --#
            camera.brightness = 45
            # Give the relative low lighting in the chamber
            camera.saturation = 5
            camera.contrast = 5
            camera.sharpness = 10
            # Increase sharpness

            # Set up white balance
            g = camera.awb_gains
            camera.awb_mode = 'auto'  # Switch to 'off' can have direct control
            camera.awb_gains = g
            # Wait for the automatic gain control to settle

            # Define shutter speed and exposure mode
            camera.shutter_speed = camera.exposure_speed
            # use fixed expose value
            camera.exposure_mode = 'auto'

            # Define resolution
              # 24 frames
            # Longer exposure time gives better image quality
            # -- Finish setting up Camera --#

            # Imaging starts
              # Stablise the camera for imaging

            # Taking an image
            try:
                camera.resolution = (3280, 2464)
                camera.framerate = 1
                camera.start_preview()
                time.sleep(10)
                camera.capture(filename)
            except Exception as e:
                print('Failed to take 8MP image, resetting to 5MP')
                camera.resolution = (2592, 1944)
                camera.framerate = 1
                camera.start_preview()
                time.sleep(10)
                camera.capture(filename)


            camera.stop_preview()

            capturedFiles = []

            capturedFiles.append(filename)
            #
            # exp_min = 10
            # exp_max = 90
            # nimages = 5
            #
            # exp_step = (exp_max - exp_min) / (nimages - 1)
            #
            # exp_step = (exp_max - exp_min) / (nimages - 1)
            # exposures = range(exp_min, exp_max + 1, exp_step)
            #
            # for step in exposures:
            #     # Set filename based on exposure
            #     fname = 'e%d.jpg' % (step)
            #     fnames.append(fname)
            #     # Set camera properties and capture
            #     camera.brightness = step
            #     camera.capture(fname)
            # return fnames

            return capturedFiles

#
# Capture by ethernet camera
#

class EthernetCamera(Camera):

    CAMERA_ADDRESS = '192.168.100.100'
    CAMERA_PORT = '1018'
    CAMERA_USER = 'admin'
    CAMERA_PWD = 'admin'
    CAMERA_WSDL = '/usr/local/wsdl'

    def __init__(self):

        super(EthernetCamera, self).__init__()

        self.camera = ONVIFCamera(EthernetCamera.CAMERA_ADDRESS, EthernetCamera.CAMERA_PORT, EthernetCamera.CAMERA_USER, EthernetCamera.CAMERA_PWD, EthernetCamera.CAMERA_WSDL)
        mediaservice = self.camera.create_media_service()
        self.snaphoturi = mediaservice.GetSnapshotUri()['Uri']

        if '-sn' not in self.snaphoturi:
            if not self.snaphoturi.endswith('&'):
                self.snaphoturi = self.snaphoturi + '&'
            self.snaphoturi = self.snaphoturi + '-sn'


    def capture(self, filename):

        # with open(filename, 'wb') as handle:
        #     response = requests.get(self.snaphoturi, stream=True)
        #     if not response.ok:
        #         print response
        #     for block in response.iter_content(1024):
        #         if not block:
        #             break
        #         handle.write(block)
        return
#
# Capture by USB camera
#

class USBCamera(Camera):


    def __init__(self):
        super(USBCamera, self).__init__()

        commands = []

        commands.append("--resolution 2592x1944")
        commands.append("--fps 24")
        commands.append("--delay 9")
        commands.append("--skip 5")
        commands.append("--frames 1")
        commands.append("--no-banner")
        commands.append("--jpeg 100")


        self.commandstring = "fswebcam "

        for cmd in commands:
            self.commandstring = self.commandstring + cmd + " "

    def capture(self, filename):
        self.setupCamera()
        files = []
        print(self.commandstring)
        try:
            files.append(filename + '_YUYV.jpg')
            cmdstring = self.commandstring + '--palette YUYV ' + filename + '_YUYV.jpg'
            os.system(cmdstring)
            files.append(filename + '_MJPG.jpg')
            cmdstring = self.commandstring + filename + '_MJPG.jpg'
            os.system(cmdstring)
        except Exception as e:
            print(e)
        return files

    def getCameraSettings(self):
        super(USBCamera, self).getCameraSettings()

        def createSetting(command='', min=0, max=0, default=0, auto='',label=''):
            setting = {}

            setting['command'] = command
            setting['min'] = min
            setting['max'] = max
            setting['default'] = default
            setting['auto'] = auto
            setting['label'] = label

            config = Utilities.getConfig()

            if auto == '':
                setting['auto_state'] = 'false'
            else:
                if 'camera' not in config:
                    config['camera'] = {}
                if command + 'auto_state' not in config['camera']:
                    config['camera'][command + 'auto_state'] = 'true'
                setting['auto_state'] = config['camera'][command + 'auto_state']

            if command + 'value' not in config['camera']:
                config['camera'][command + 'value'] = default
            setting['value'] = config['camera'][command + 'value']

            Utilities.setConfig(config)

            return setting

        self.camera_settings = []

        self.camera_settings.append(createSetting(command='exposure_absolute',min=4, max=5000, default=625, label='Exposure (4 - 5000)', auto='exposure_auto'))
        self.camera_settings.append(createSetting(command='focus_absolute',min=0, max=21, default=16, label='Focus (0 - 21)', auto='focus_auto'))
        self.camera_settings.append(createSetting(command='brightness',min=0, max=15, default=8, label='Brightness (0 - 15)'))
        self.camera_settings.append(createSetting(command='saturation',min=0, max=15, default=7, label='Saturation (0 - 15)'))
        self.camera_settings.append(createSetting(command='hue',min=-10, max=10, default=0, label='Hue (-10 - 10)'))
        self.camera_settings.append(createSetting(command='gamma',min=1, max=10, default=7, label='Gamma (1 -  10)'))
        self.camera_settings.append(createSetting(command='sharpness',min=0, max=15, default=6, label='Sharpness (0 - 15)'))
        self.camera_settings.append(createSetting(command='contrast',min=0, max=15, default=8, label='Contrast (0 - 15)'))

        return self.camera_settings




    def setupCamera(self):
        config = Utilities.getConfig()
        if 'camera' not in config:
            return

        self.getCameraSettings()

        for setting in self.camera_settings:
            if setting['command'] + 'auto_state' in config['camera']:
                if setting['auto'] != '':
                    if 'exposure' in setting['command']:
                        if config['camera'][setting['command'] + 'auto_state'] == 'true':
                            print("sudo v4l2-ctl -d 0 --set-ctrl=" + setting['auto'] + "=3")
                            os.system("sudo v4l2-ctl -d 0 --set-ctrl=" + setting['auto'] + "=3")
                        else:
                            print("sudo v4l2-ctl -d 0 --set-ctrl=" + setting['auto'] + "=1")
                            os.system("sudo v4l2-ctl -d 0 --set-ctrl=" + setting['auto'] + "=1")
                    else:
                        if config['camera'][setting['command'] + 'auto_state'] == 'true':
                            print("sudo v4l2-ctl -d 0 --set-ctrl=" + setting['auto'] + "=1")
                            os.system("sudo v4l2-ctl -d 0 --set-ctrl=" + setting['auto'] + "=1")
                        else:
                            print("sudo v4l2-ctl -d 0 --set-ctrl=" + setting['auto'] + "=0")
                            os.system("sudo v4l2-ctl -d 0 --set-ctrl=" + setting['auto'] + "=0")

            if setting['command'] + 'value' in config['camera']:
                print("sudo v4l2-ctl -d 0 --set-ctrl=" + setting['command'] + "=" + str(config['camera'][setting['command'] + 'value']))
                os.system("sudo v4l2-ctl -d 0 --set-ctrl=" + setting['command'] + "=" + str(config['camera'][setting['command'] + 'value']))



