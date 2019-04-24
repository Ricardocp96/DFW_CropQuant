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

import json
from pistatus import PiStatus
import time

# Abstract class defining structure
class DataTransmit:
    def __init__(self):
        raise NotImplementedError()

    def transmit(self, data):
        raise NotImplementedError()

    def available(self):
        raise NotImplementedError()

import requests

# Object facilitates POST transfer through HTTP
class HTTPTransmit(DataTransmit):

    # setup host
    def __init__(self, target, username=None, password=None):

        if username is None:
            self.target = target
        else:
            self.target = target + '?' + username + '=' + password

    # send data
    def transmit(self, data):

        print(data)

        deviceid = '&macaddress=' + PiStatus.getMACAddress()

        r = requests.post(self.target + deviceid, data=json.dumps(data))
        print('--- RESPONSE TEXT ---')
        print(r.text)
        print('--- RESPONSE TEXT ---')
        return r.status_code

    def upload(self, filepath, filename):

        files = {'file': (filename, open(filepath, 'rb'), 'multipart/form-data')}

        deviceid = '&macaddress=' + PiStatus.getMACAddress()

        print()

        r = requests.post(self.target + deviceid, files=files)

        print('--- RESPONSE TEXT ---')
        print(r.text)
        print('--- RESPONSE TEXT ---')
        return r.status_code

    # check if available by sending test request and reading response code
    def available(self):
        return True
        avail = False
        i = 0

        while i < 10 and not avail:
            i += 1
            try:
                r = requests.get(self.target + "&ping=test")
                if r.status_code < 300:

                    avail = True
                else:
                    print('Response: ' + str(r.status_code))
            except Exception as e:
                print(e)
            time.sleep(5)

        return avail