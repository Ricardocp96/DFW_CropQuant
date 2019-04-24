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

from interface import Interface
from flask import Flask
from flask import render_template
from flask import url_for
from flask import request
from flask import send_file
from utilities import Utilities
from werkzeug.utils import secure_filename
import time
from monitoring.pistatus import PiStatus
from imaging.camera import Camera
import csv
import os
import subprocess
import requests
from scheduling.scheduler import Scheduler

from utilities import Utilities
# from monitoring.server import Server
from monitoring.datatransmit import HTTPTransmit

from shutil import copyfile

class WebInterface(Interface):



    def __init__(self, modules):
        self.port = 8082
        self.modules = modules

        self.streamactive = False

        self.customheight = 1.5

        self.adjustingcam = False

        self.upload_folder = '/tmp/cropquant/upload'

        if not os.path.exists(self.upload_folder):
            os.makedirs(self.upload_folder, 0o0755)


    def videostream(self, command=False):
        if command == self.streamactive:
            return
        try:
            if command:
                os.system("sudo service motion start")
                self.streamactive = True
            else:
                os.system("sudo service motion stop")
                self.streamactive = False
        except:
            self.streamactive = False
            return

    def upload_file(self, request, allowed=[]):
        if request.method != 'POST':
            print('not post')
            return ''

        print(request)
        print(request.files)

        if 'file' not in request.files:
            print('file not in request')
            return ''

        file = request.files['file']

        if file.filename == '':
            print('filename empty')
            return ''

        if len(allowed) > 0:
            found = False
            for ext in allowed:
                if file.filename.lower().endswith(ext.lower()):
                    found = True
            if not found:
                print('not allowed extension')
                return ''

        filename = secure_filename(file.filename)
        file.save(os.path.join(self.app.config['UPLOAD_FOLDER'], filename))

        return os.path.join(self.app.config['UPLOAD_FOLDER'], filename), filename

    def getStreamIP(self):
        ip = request.remote_addr


        return PiStatus.getIPAddress()

    def experimentPage(self):

        data = {}

        data['experiment'] = 'Unnamed_Experiment'
        data['deviceid'] = Utilities.getSerial()
        data['replicate'] = '01'
        data['duration'] = '220'
        data['imageid'] = 0
        data['imageschedule'] = 0
        data['sensorschedule'] = 0

        try:
            data['endtime'] = time.time() + int(int(data['duration']) * 60 * 60 * 24)
        except:
            data['endtime'] = time.time()

        data['endtime'] = time.strftime("%d.%m.%Y", time.gmtime(int(data['endtime'])))

        config = Utilities.getConfig()

        if 'capture' in config:
            if 'experiment' in config['capture']:
                data['experiment'] = config['capture']['experiment']
            if 'deviceid' in config['capture']:
                data['deviceid'] = config['capture']['deviceid']
            if 'replicate' in config['capture']:
                data['replicate'] = config['capture']['replicate']
            if 'duration' in config['capture']:
                data['duration'] = config['capture']['duration']
            if 'endtime' in config['capture']:
                data['endtime'] = config['capture']['endtime']
            if 'imageid' in config['capture']:
                data['imageid'] = config['capture']['imageid']

        #print config['schedule']

        if 'schedule' in config:
            if 'image' in config['schedule']:
                data['imageschedule'] = config['schedule']['image']
            if 'sensor' in config['schedule']:
                data['sensorschedule'] = config['schedule']['sensor']
            if 'overview' in config['schedule']:
                data['overviewschedule'] = config['schedule']['overview']

        if data['deviceid'] == '':
            data['deviceid'] = Utilities.getSerial()

        stream = 'False'
        if self.streamactive:
            stream = 'True'

        return render_template('experiment.html',data=data,latestimage=url_for('static', filename='latest.jpg'),stream=stream,ip=self.getStreamIP())

    def saveExperimentData(self, formdata):
        config = Utilities.getConfig()

        if 'capture' not in config:
            config['capture'] = {}
            config['capture']['experiment'] = ''
            config['capture']['deviceid'] = ''
            config['capture']['replicate'] = ''
            config['capture']['duration'] = 0
            config['capture']['endtime'] = ''
            config['capture']['imageid'] = 0

        if 'experiment' in formdata:
            config['capture']['experiment'] = formdata['experiment']
        if 'deviceid' in formdata:
            config['capture']['deviceid'] = formdata['deviceid']
        if 'replicate' in formdata:
            config['capture']['replicate'] = formdata['replicate']
        if 'duration' in formdata:
            config['capture']['duration'] = formdata['duration']
        if 'endtime' in formdata:
            try:
                config['capture']['capture']['endtime'] = time.time() + int(int(config['capture']['duration']) * 60 * 60 * 24)
            except:
                config['capture']['endtime'] = ''
        if 'imageid' in formdata:
            config['capture']['imageid'] = formdata['imageid']

        Utilities.saveConfig()

    def saveSchedule(self, formdata):

        config = Utilities.getConfig()

        if 'schedule' not in config:
            config['schedule'] = {}
            config['schedule']['image'] = 0
            config['schedule']['sensor'] = 0
            config['schedule']['overview'] = []

        if 'schedule_image' in formdata:
            config['schedule']['image'] = formdata['schedule_image']
        if 'schedule_sensor' in formdata:
            config['schedule']['sensor'] = formdata['schedule_sensor']


        Utilities.saveConfig()

        Scheduler.shedule()

    def csvtosqldate(self, date):
        try:
            parts = date.split(' ')

            d = parts[0].split('.')

            sqldate = d[2] + '-' + d[1] + '-' + d[0] + ' ' + parts[-1]
            return sqldate
        except:
            return date

    def parseCSV(self, csvFile, column):
        data = []

        with open(csvFile, 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')

            head = True

            for row in csvreader:
                if head:
                    head = False
                else:
                    data.append([self.csvtosqldate(row[0]), row[column]])

        return data

    def sensorPage(self, graph=''):

        selectedgraph = graph

        if selectedgraph == '':
            selectedgraph = 'temp'

        graphinfo = {}

        graphinfo['temp'] = {'slug':'temp', 'link': 'Temperature', 'title':'Temperature (C)', 'unit':'C', 'column':1}
        graphinfo['humid'] = {'slug': 'humid', 'link': 'Humidity',  'title': 'Humidity (%)', 'unit':'C', 'column':2}
        graphinfo['light'] = {'slug': 'light', 'link': 'Light',  'title': 'Light Levels (%)', 'unit':'%', 'column':3}
        graphinfo['soiltemp'] = {'slug': 'soiltemp', 'link': 'Soil Temp',  'title': 'Soil Temperature (C)', 'unit':'C', 'column':4}
        graphinfo['soilhumid'] = {'slug': 'soilhumid', 'link': 'Soil Humidity',  'title': 'Soil Humidity (%)', 'unit':'%', 'column':5}


        graphdata = self.parseCSV( Utilities.getConfigFolderItem('sensorlog.csv'), graphinfo[selectedgraph]['column'])


        status = PiStatus.getPiStatus(False)
        return render_template('sensor.html',graphdata=graphdata,graphinfo=graphinfo,selectedgraph=selectedgraph,status=status)

    # def float_to_hex4(self, f):
    #     result = []
    #     for c in struct.pack('<f', f):
    #         result.append(ord(c))
    #
    #     return result

    def systemPage(self, graph=''):

        selectedgraph = graph

        if selectedgraph == '':
            selectedgraph = 'cpuuse'

        graphinfo = {}

        graphinfo['cpuuse'] = {'slug':'cpuuse', 'link': 'CPU Usage', 'title':'CPU Usage (%)', 'unit':'%', 'column':2}
        graphinfo['cputemp'] = {'slug': 'cputemp', 'link': 'CPU Temp',  'title': 'CPU Temperature (C)', 'unit':'C', 'column':1}
        graphinfo['memuse'] = {'slug': 'memuse', 'link': 'Mem Usage',  'title': 'RAM Usage (%)', 'unit':'%', 'column':3}


        graphdata = self.parseCSV( Utilities.getSystemLogCSV(), graphinfo[selectedgraph]['column'])


        status = PiStatus.getPiStatus(False)
        return render_template('system.html',graphdata=graphdata,graphinfo=graphinfo,selectedgraph=selectedgraph,status=status)



    def cameraPage(self):
        camera_settings = Camera.getInstance().getCameraSettings()
        print(camera_settings)
        return render_template('camera.html',ipaddress=self.getStreamIP(),camerasettings=camera_settings)

    def makeHeader(self):
        mods = []

        sensors = 'false'

        if os.path.isfile(Utilities.getConfigFolderItem('sensorlog.csv')):
            sensors = 'true'

        for mod in self.modules:
            mods.append({'name': mod.getName(), 'slug': mod.getSlug()})

        return render_template('header.html', css=url_for('static', filename='style.css'),
                               ei=url_for('static', filename='eilogo.png'),
                               jic=url_for('static', filename='jiclogo.png'),
                               jquery=url_for('static', filename='jquery.js'),
                               datatables=url_for('static', filename='datatables.js'),
                               d3=url_for('static', filename='d3.js'),
                               logo=url_for('static', filename='logo.png'),
                               font=url_for('static', filename='robotolight.ttf'),
                               datatablescss=url_for('static', filename='datatables.css'),modules=mods,sensors=sensors)

    def makeFooter(self):
        return render_template('footer.html')



    def systemShutdown(self):
        print("System Shutting Down")

        Utilities.releaseLockFile("Shutdown")
        subprocess.Popen(["sudo", "shutdown", "-h", "now"])
        return render_template('shutdown.html')



    def setCameraValue(self, name, value):

        print("Adjusting: " + name)

        if self.adjustingcam:
            print("conflict!")
            return

        val = int(value)

        self.adjustingcam = True

        try:
            config = Utilities.getConfig()

            if 'camera' not in config:
                config['camera'] = {}

            setting = Camera.getInstance().getCameraSetting(name)

            if setting['auto'] != '':

                config['camera'][name + 'auto_state'] = 'true'

                if 'exposure' in setting['auto']:
                    os.system("sudo v4l2-ctl -d 0 --set-ctrl=" + setting['auto'] + "=1")
                else:
                    os.system("sudo v4l2-ctl -d 0 --set-ctrl=" + setting['auto'] + "=0")

            config['camera'][name + 'value'] = val

            Utilities.setConfig(config)

            os.system("sudo v4l2-ctl -d 0 --set-ctrl=" + name + "=" + str(val))


        except Exception as e:
            print(e)

        self.adjustingcam = False

        print("Camera Setting Set: " + name + " - " + str(value))

    def setCameraAuto(self, name, state):
        if self.adjustingcam:
            return

        self.adjustingcam = True

        try:
            config = Utilities.getConfig()

            if 'camera' not in config:
                config['camera'] = {}

            setting = Camera.getInstance().getCameraSetting(name)

            if state:
                config['camera'][name + 'auto_state'] = 'true'
            else:
                config['camera'][name + 'auto_state'] = 'false'

            Utilities.setConfig(config)

            if state:
                if 'exposure' in setting['auto']:
                    os.system("sudo v4l2-ctl -d 0 --set-ctrl=" + setting['auto'] + "=3")
                else:
                    os.system("sudo v4l2-ctl -d 0 --set-ctrl=" + setting['auto'] + "=1")
            else:
                if 'exposure' in setting['auto']:
                    os.system("sudo v4l2-ctl -d 0 --set-ctrl=" + setting['auto'] + "=1")
                else:
                    os.system("sudo v4l2-ctl -d 0 --set-ctrl=" + setting['auto'] + "=0")
        except Exception as e:
            print(e)

        self.adjustingcam = False

    def start(self):

        app = Flask(__name__)
        app.debug = True


        @app.route('/stream')
        def streampage():
            if self.streamactive:
                self.videostream(False)
            else:
                self.videostream(True)

            return self.makeHeader() + self.experimentPage() + self.makeFooter()


        @app.route('/experiment', methods=['GET', 'POST'])
        @app.route("/", methods=['GET', 'POST'])
        def experimentpage():
            self.videostream(False)
            if request.method == 'POST':
                if 'experiment' in request.form:
                    self.saveExperimentData(request.form)
                    self.saveSchedule(request.form)
            return self.makeHeader() + self.experimentPage() + self.makeFooter()

        @app.route("/schedule")
        def experimentschedulepage():
            self.videostream(False)
            return self.makeHeader() + self.experimentPage() + self.makeFooter()

        @app.route('/setcameravalue/<name>/<val>')
        def setCamVal(name,val):
            self.setCameraValue(name,int(val))
            return ""

        @app.route('/setcameraauto/<name>/<val>')
        def setCameraAuto(name,val):
            state = False
            if val == 'true':
                state = True

            self.setCameraAuto(name,state)
            return ""

        @app.route('/system/<graph>')
        def systempagegraph(graph):
            self.videostream(False)
            return self.makeHeader() + self.systemPage(graph) + self.makeFooter()

        @app.route('/system')
        def systempage():
            self.videostream(False)
            return self.makeHeader() + self.systemPage() + self.makeFooter()

        @app.route('/camera')
        def camerapage():
            self.videostream(True)
            return self.makeHeader() + self.cameraPage() + self.makeFooter()

        @app.route('/sensor/<graph>')
        def sensorpagegraph(graph):
            self.videostream(False)
            return self.makeHeader() + self.sensorPage(graph) + self.makeFooter()

        @app.route('/sensor')
        def sensorpage():
            self.videostream(False)
            return self.makeHeader() + self.sensorPage() + self.makeFooter()


        @app.route('/shutdown')
        def shutdown():
            self.videostream(False)
            return self.systemShutdown()

        @app.route('/downloadcsv')
        def downloadsensordata():
            self.videostream(False)
            return send_file('/cropquant/sensorlog.csv',
                             mimetype='text/csv',
                             attachment_filename='SensorData.csv',
                             as_attachment=True)

        @app.route('/update', methods=['GET', 'POST'])
        def update():

            if request.method == 'POST':

                uploaded_filepath, uploaded_filename = self.upload_file(request, ['cq'])
                if uploaded_filename != '':
                    os.rename(uploaded_filepath, os.path.join('/cropquant', 'update.cq'))
                    print('Rebooting')
                    os.system("sudo shutdown -r now")

                    return "<h1>System is rebooting...<h1>"


            return render_template('update.html')

        @app.route('/reboot')
        def reboot():
            self.videostream(False)
            os.system("sudo shutdown -r now")

        @app.route('/module/<moduleslug>')
        def modulepage(moduleslug):
            self.videostream(False)
            for mod in self.modules:
                if moduleslug == mod.getSlug():
                    return self.makeHeader() + mod.interfaceWeb('index') + self.makeFooter()

            return self.makeHeader() + 'Module Not Found' + self.makeFooter()

        @app.route('/stopinterface/<key>')
        def stopInterface(key):
            if key == 'vmgwBz67QV55kLqKen3LTUbj':
                exit(0)

        @app.route('/datainput.php?<dev_key>=<dev_val>', methods=['GET', 'POST'])
        def datainput(dev_key, dev_val):

            data = request.get_json()

            child_node = {}

            child_node['macaddress'] = data['macaddress']
            child_node['hostname'] = data['hostname']
            child_node['ipaddress'] = data['ipaddress']

            config = Utilities.getConfig()

            if 'children' not in config:
                config['children'] = []

            config['children'].append(child_node)

            Utilities.setConfig(config)

            transmitter = HTTPTransmit(Utilities.get_server_ip() + "/" + 'datainput.php', dev_key,dev_val)
            retCode = transmitter.transmit(data)
            print("transmitted status with return code " + str(retCode))

        app.config['UPLOAD_FOLDER'] = self.upload_folder
        app.run(host="0.0.0.0",port=self.port)

