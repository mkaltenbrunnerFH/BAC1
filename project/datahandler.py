from threading import Thread, Event
from PyQt5.QtGui import QStandardItem
import requests
import json
import queue


class DataHandler(Thread):
    def __init__(self, queue, lock, drpdMenu, rootNode, vendor_for_mac, macs_per_ssid, ssids_per_mac):
        super().__init__()
        self.daemon = True
        self.queue = queue
        self.lock = lock
        self.stopRequest = Event()
        self.drpdMenu = drpdMenu
        self.rootNode = rootNode
        self.vendor_for_mac = vendor_for_mac
        self.macs_per_ssid = macs_per_ssid
        self.ssids_per_mac = ssids_per_mac

    def run(self):
        while not self.stopRequest.isSet():
            try:
                mac_and_ssid = self.queue.get(True, 0.05)
                mac = mac_and_ssid[0]
                ssid = mac_and_ssid[1].decode('utf-8')
                self.vendor_lookup(mac)
                self.update_dicts_and_view(mac, ssid)
            except queue.Empty:
                continue

    def join(self, timeout=None):
        self.stopRequest.set()
        super().join(timeout)

    def vendor_lookup(self, mac):
        # GET VENDOR
        # if mac not known, then check vendor via API
        if mac not in self.vendor_for_mac:
            r = requests.get("https://macvendors.co/api/%s" % mac)
            req = json.loads(r.content)
            try:
                vendor = req['result']['company']
            except KeyError:
                vendor = "Unknown Vendor"
            self.vendor_for_mac[mac] = vendor

    def update_dicts_and_view(self, mac, ssid):
        # UPDATE dictionary where key is SSID
        # if ssid not known, create array for macs
        if ssid not in self.macs_per_ssid:
            self.macs_per_ssid[ssid] = list()
            self.macs_per_ssid[ssid].append(mac)

            if self.drpdMenu.currentIndex() == 0:
                # insert new parent item in list
                new_item = QStandardItem(ssid)
                new_item.setEditable(False)
                new_child_item = QStandardItem(mac + " - " + self.vendor_for_mac[mac])
                new_child_item.setEditable(False)
                new_item.appendRow(new_child_item)
                self.rootNode.appendRow(new_item)
        else:
            self.macs_per_ssid[ssid].append(mac)
            if self.drpdMenu.currentIndex() == 0:
                for i in range(self.rootNode.rowCount()):
                    item = self.rootNode.child(i)
                    if item.text() == ssid:
                        new_child_item = QStandardItem(mac + " - " + self.vendor_for_mac[mac])
                        new_child_item.setEditable(False)
                        item.appendRow(new_child_item)

        # UPDATE dictionary where key is MAC
        # if mac not known, create array for ssids
        if mac not in self.ssids_per_mac:
            self.ssids_per_mac[mac] = list()
            self.ssids_per_mac[mac].append(ssid)

            if self.drpdMenu.currentIndex() == 1:
                # insert new parent item in list
                new_item = QStandardItem(mac + " - " + self.vendor_for_mac[mac])
                new_item.setEditable(False)
                new_child_item = QStandardItem(ssid)
                new_child_item.setEditable(False)
                new_item.appendRow(new_child_item)
                self.rootNode.appendRow(new_item)
        else:
            self.ssids_per_mac[mac].append(ssid)
            if self.drpdMenu.currentIndex() == 1:
                for i in range(self.rootNode.rowCount()):
                    item = self.rootNode.child(i)
                    if item.text() == (mac + " - " + self.vendor_for_mac[mac]):
                        new_child_item = QStandardItem(ssid)
                        new_child_item.setEditable(False)
                        item.appendRow(new_child_item)
