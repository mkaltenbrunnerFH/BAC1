#authors: Leonhard Jauch, Michael Kaltenbrunner, Tobias Pfeiffer
#university of applied sciences Salzburg, ITS-B2017

from PyQt5.QtCore import QThread
import requests
import json
import queue
import datetime


# src: https://www.youtube.com/watch?v=o81Q3oyz6rg
class DataHandler(QThread):

    def __init__(self, queue, lock, update_list_view, renew_probe, vendor_for_mac, macs_per_ssid, ssids_per_mac):
        super().__init__()
        self.daemon = True
        self.queue = queue
        self.dict_lock = lock
        self.update_list_view = update_list_view
        self.renew_probe = renew_probe
        self.probes = set()
        self.vendor_for_mac = vendor_for_mac
        self.macs_per_ssid = macs_per_ssid
        self.ssids_per_mac = ssids_per_mac

    def run(self):
        while True:
            # src: https://eli.thegreenplace.net/2011/12/27/python-threads-communication-and-stopping/
            try:
                data = self.queue.get(True, 0.05)
                mac = data[0]
                ssid = data[1].decode('utf-8')
                power = data[2]
                # src: https://stackoverflow.com/questions/415511/how-to-get-the-current-time-in-python
                timestamp = str(datetime.datetime.now()).split(' ')[1]
                self.vendor_lookup(mac)
                self.update_dicts_and_view(mac, ssid, timestamp, power)
            except queue.Empty:
                continue

    def join(self, timeout=None):
        self.stopRequest.set()
        super().join(timeout)

    def vendor_lookup(self, mac):
        # GET VENDOR
        # if mac not known, then check vendor via API
        if mac not in self.vendor_for_mac:
            # src: https://macvendors.co/api/python
            r = requests.get("https://macvendors.co/api/%s" % mac)
            req = json.loads(r.content)
            try:
                vendor = req['result']['company']
            except KeyError:
                vendor = "Unknown Vendor"
            self.dict_lock.acquire()
            self.vendor_for_mac[mac] = vendor
            self.dict_lock.release()

    def update_dicts_and_view(self, mac, ssid, timestamp, power):

        extra_info = {'timestamp': timestamp, 'power': power}

        self.dict_lock.acquire()

        if (mac, ssid) in self.probes:
            self.macs_per_ssid[ssid][mac] = extra_info
            self.ssids_per_mac[mac][ssid] = extra_info
            self.dict_lock.release()
            self.renew_probe.emit(mac, ssid, timestamp, power)

        else:
            mac_existed = False
            ssid_existed = False

            # UPDATE dictionary where key is SSID
            # if ssid not known, create dict for macs
            if ssid not in self.macs_per_ssid:
                self.macs_per_ssid[ssid] = dict()
                self.macs_per_ssid[ssid][mac] = extra_info
            else:
                ssid_existed = True
                self.macs_per_ssid[ssid][mac] = extra_info

            # UPDATE dictionary where key is MAC
            # if mac not known, create dict for ssids
            if mac not in self.ssids_per_mac:
                self.ssids_per_mac[mac] = dict()
                self.ssids_per_mac[mac][ssid] = extra_info
            else:
                mac_existed = True
                self.ssids_per_mac[mac][ssid] = extra_info

            self.probes.add((mac, ssid))
            self.dict_lock.release()
            self.update_list_view.emit(mac, ssid, timestamp, power, mac_existed, ssid_existed)
