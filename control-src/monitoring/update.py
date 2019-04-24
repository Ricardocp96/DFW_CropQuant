import os
import requests
from monitoring.server import Server

class Update():


    def __init__(self):
        return

    def download_update(self):
        url = Server.getServerIP() + '/update.cq'

        download = os.path.join('/cropquant', 'update/cq')

        r = requests.get(url, allow_redirects=True)

        with open(download, 'wb') as download_file:
            download_file.write(r.content)