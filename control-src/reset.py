import os
import random
from scheduling.scheduler import Scheduler

class FactoryReset:

    @staticmethod
    def reset():

        print("WARNING: Factory Reset will reset all settings and REMOVE ALL DATA.")

        FactoryReset.auth()

        # Remove settings
        os.system("sudo rm -rf /cropquant/*")

        # Remove desktop image store
        os.system("sudo rm -rf /home/pi/Desktop/*")

        # Remove Image Data on USB
        if os.path.exists("/media/CROPQUANT"):
            os.system("sudo rm -rf /media/CROPQUANT/*")

        if os.path.exists("/media/pi/CROPQUANT"):
            os.system("sudo rm -rf /media/pi/CROPQUANT/*")

        # Remove Scheduled Taskssud
        Scheduler.remove("status")
        Scheduler.remove("capture")
        Scheduler.remove("imageupload")
        Scheduler.remove("overviewcapture")

        print("Reset to factory settings")

    @staticmethod
    def auth():

        code = random.randint(10000000,99999999)
        entered = input("Enter code to continue: " + str(code) + ": ")

        if code == int(entered):
            print("Reset authorised")
        else:
            print("Authentication failed")
            exit(1)