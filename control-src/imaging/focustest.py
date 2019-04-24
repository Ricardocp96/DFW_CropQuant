from camera import Camera
import os

class FocusTest(object):

    @staticmethod
    def Run():

        commands = []

        commands.append("--resolution 2592x1944")
        commands.append("--fps 24")
        commands.append("--delay 9")
        commands.append("--skip 5")
        commands.append("--frames 1")
        commands.append("--no-banner")

        commands.append("--jpeg 100")

        commands.append("--palette YUYV")

        commandstring = "fswebcam "

        for cmd in commands:
            commandstring = commandstring + cmd + " "

        filename = '/home/pi/Desktop/'

        os.system('sudo v4l2-ctl -d 0 --set-ctrl=focus_auto=0')

        for i in range(0,22):

            os.system('sudo v4l2-ctl -d 0 --set-ctrl=focus_absolute=' + str(i))

            os.system(commandstring + filename + 'focustest_' + str(i) + '.jpg')


        os.system('sudo v4l2-ctl -d 0 --set-ctrl=focus_auto=1')
		
		
