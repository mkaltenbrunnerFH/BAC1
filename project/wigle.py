from PyQt5.QtCore import QThread
from configparser import ConfigParser
import requests
import queue


# src: https://www.youtube.com/watch?v=o81Q3oyz6rg
class Wigle(QThread):
    def __init__(self, queue, map_update, no_results):
        super().__init__()
        self.daemon = True
        self.queue = queue
        self.map_update = map_update
        self.no_results = no_results
        # src: https://github.com/glennzw/WigleAPI/blob/master/wigle_api.py
        Config = ConfigParser()
        Config.read('wigle.conf')
        try:
            api_name = Config.get('wigle', 'user')
            api_token = Config.get('wigle', 'key')
            self.auth = (api_name, api_token)
        except:
            raise ValueError('Please enter your API key into the wigle.conf file. See https://api.wigle.net')

    def run(self):
        while True:
            # src: https://eli.thegreenplace.net/2011/12/27/python-threads-communication-and-stopping/
            try:
                ssid = self.queue.get(True, 0.05)
                # src: https://github.com/mgp25/Probe-Hunter/blob/master/wigle.py
                # src: https://medium.com/@neuralnets/building-a-wifi-spots-map-of-networks-around-you-with-wigle-and-python-5adf72a48140
                r = requests.get('https://api.wigle.net/api/v2/network/search', {'ssid': ssid}, auth=self.auth)

                req = r.json()
                if req['totalResults'] <= 0:
                    self.no_results.emit(ssid)
                else:
                    resultCount = req['resultCount']
                    entries = req['results']
                    self.map_update.emit(ssid, resultCount, entries)
            except queue.Empty:
                continue
