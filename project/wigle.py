from threading import Thread
import requests
from PyQt5.QtWidgets import QMessageBox


class Wigle(Thread):
    def __init__(self, ssid, map):
        super().__init__()
        self.ssid = ssid
        self.map = map

    def run(self):
        r2 = requests.get('https://api.wigle.net/api/v2/network/search',
                          {'ssid': self.ssid, 'country': 'AT'},
                          auth=('AID0c03e6a1fdff1332213ca04110bf6cb8', '6f7ae03341051392258941eda733365c'))
        req = r2.json()
        entries = req['results']
        if req['totalResults'] == 0:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Information)
            msgBox.setWindowTitle("Warning")
            msgBox.setText("No entry for SSID '%s' found in WiGLE database." % self.ssid)
            return msgBox.exec()
        else:
            arr = req['results']
            for entry in arr:
                lat = entry['trilat']
                lon = entry['trilong']
                ssid = self.ssid
                self.map.set_marker(lat, lon, ssid)
