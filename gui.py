

import sys

from PyQt5.QtWidgets import *
import sys
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget
from pyqtlet import L, MapWidget

from PyQt5.QtGui import *

from PyQt5.QtCore import *

from scapy.all import *
from threading import RLock, Thread
import json
import requests
from time import sleep

# using API to checkout vendors by MAC
macurl = 'https://macvendors.co/api/%s'

# using API from wigle
wigleurl = 'https://api.wigle.net/api/v2/network/search'

lock = RLock()

probe_data = set()
mac2ssid = dict()
ssid2mac = dict()
detail = None
j = 0




class Color(QWidget):

 


    def __init__(self, color, *args, **kwargs):


        super(Color, self).__init__(*args, **kwargs)


        self.setAutoFillBackground(True)

 


        palette = self.palette()


        palette.setColor(QPalette.Window, QColor(color))


        self.setPalette(palette)

 

def window():


    app = QApplication(sys.argv)


    win = QWidget()


    grid = QGridLayout()

 

 


    drpdMenu = QComboBox()

    btnStart = QPushButton('Start')



    def search_prob(p):
        if p.type == 0 and p.subtype == 4 and p.info != b'':
            mac_and_ssid = (p.addr2, p.info)
            mac = p.addr2
            ssid = p.info.decode('utf-8')
            # einfügen in dictionaries
            if mac_and_ssid not in probe_data:
                r = requests.get(macurl % p.addr2)
                req = json.loads(r.content)
                try:
                    vendor = req['result']['company']
                except KeyError:
                    vendor = "Unknown"
                print(mac)
                print(ssid)
                print(vendor)
                if not ssid2mac.__contains__(ssid) and drpdMenu.currentIndex() == 0:
                    lstLeft.addItem(ssid)

                if not mac2ssid.__contains__(mac) and drpdMenu.currentIndex() == 1:
                    lstLeft.addItem(mac)

                if mac2ssid.__contains__(mac):
                    lock.acquire()
                    mac2ssid[mac].append(ssid)
                    lock.release()
                else:
                    lock.acquire()
                    mac2ssid[mac] = list()
                    mac2ssid[mac].append(ssid)
                    lock.release()

                if ssid2mac.__contains__(ssid):
                    lock.acquire()
                    ssid2mac[ssid].append(mac)
                    lock.release()
                else:
                    lock.acquire()
                    ssid2mac[ssid] = list()
                    ssid2mac[ssid].append(mac)
                    lock.release()

                print("SSID = %s, Src = %s, Vendor = %s" % (p.info, p.addr2, vendor))
                probe_data.add(mac_and_ssid)
                print(mac2ssid)
                print('----------------------------------------------------------------------------')
                print(ssid2mac)

    def sniff():
        btnStart.setEnabled(False)
        sniffer = Sniffer()
        sniffer.start()

    class Sniffer(Thread):
        #  def  __init__(self, interface="eth0"):
        #     super().__init__()

        #        self.interface = interface

        def run(self):
            scapy.all.sniff(iface="wlan0mon", prn=search_prob)


    btnStart.clicked.connect(sniff)
    btnWigle = QPushButton('Check Database')


    class Wigler(Thread):
        def run(self):
            if drpdMenu.currentIndex() == 0:
                ssid = lstLeft.currentItem().text()
            elif drpdMenu.currentIndex() == 1:
                ssid = lstRight.currentItem().text()
            r2 = requests.get(wigleurl, {'ssid': ssid, 'country': 'AT'},
                              auth=('AID0c03e6a1fdff1332213ca04110bf6cb8', '6f7ae03341051392258941eda733365c'))
            global detail
            detail = r2.json()

    def wig():
        wigler = Wigler()
        wigler.start()
        wigler.join()
        global detail
        #remove markers
        if detail['totalResults'] == 0:
            msgBox = QMessageBox()
            msgBox.setText("No Entry found in WiGLE Database")
            msgBox.exec()
        else:
            arr = detail['results']
            for entry in arr:
                lat = entry['trilat']
                lon = entry['trilong']
                ssid = entry['ssid']
                widget.MapUpdate(lat, lon, ssid)


    btnWigle.clicked.connect(wig)

    def fillListItems():
        lstRight.clear()
        key = lstLeft.currentItem().text()
        try:
            if drpdMenu.currentIndex() == 0:
                macs = ssid2mac[key]
                for mac in macs:
                    lstRight.addItem(mac)
            elif drpdMenu.currentIndex() == 1:
                ssids = mac2ssid[key]
                for ssid in ssids:
                    lstRight.addItem(ssid)
        except KeyError:
            pass


    lstLeft = QListWidget()

    lstLeft.itemSelectionChanged.connect(fillListItems)

    lstRight = QListWidget()


    lbPlaceholder = QLabel("Platzhalter")


    lbLeft = QLabel("SSID:")


    lbRight = QLabel("MAC Adress:")

 


    lbLeft.setAlignment(Qt.AlignBottom)


    lbRight.setAlignment(Qt.AlignBottom)

 


    btnStart.setToolTip('start/stop scanning for probe requests.')


    btnWigle.setToolTip('Check WiGLE Database for selected SSID.')


    drpdMenu.addItem("MACS per SSID")
    drpdMenu.addItem("SSIDs per MAC")

    def selectionchange():
        lstLeft.clear()
        lstRight.clear()
        if drpdMenu.currentIndex() == 0:
            lbLeft.setText("SSIDs")
            lbRight.setText("MACs")
            #update fields
            for key in ssid2mac.keys():
                lstLeft.addItem(key)
        elif drpdMenu.currentIndex() == 1:
            lbLeft.setText("MACs")
            lbRight.setText("SSIDs")
            for key in mac2ssid.keys():
                lstLeft.addItem(key)


    drpdMenu.currentIndexChanged.connect(selectionchange)


    drpdMenu.setToolTip('group results by...')

 


    #grid.addWidget(Color('blue'), 0, 0)


    grid.addWidget(lbPlaceholder, 0, 0)


    #grid.addWidget(Color('red'), 0, 9)


    #grid.addWidget(Color('yellow'), 9, 0)


    grid.addWidget(lbPlaceholder, 9, 0)


    #grid.addWidget(Color('lime'), 9, 9)

 


    #zeile, spalte, rowspan, colspan#


    #grid.addWidget(Color('red'), 0, 0)

 


    grid.addWidget(btnStart, 0, 1)


    grid.addWidget(btnWigle, 8, 1)

 


    grid.addWidget(drpdMenu, 1, 1)

 


    #grid.setAlignment(lbMac)


    grid.addWidget(lbLeft, 2, 0)


    grid.addWidget(lbRight, 2, 1)

 

 


    grid.addWidget(lstLeft, 3, 0, 4, 2)


    grid.addWidget(lstRight, 3, 1, 4, 2)


    #grid.addWidget(lbPlaceholder, 2, 1)

 


    #grid.addWidget(Color('green'), 3, 0)

    class MapWindow(QWidget):
        def __init__(self):
            # Setting up the widgets and layout
            super().__init__()
            self.mapWidget = MapWidget()
            self.layout = QVBoxLayout()
            self.layout.addWidget(self.mapWidget)
            self.setLayout(self.layout)

            # Working with the maps with pyqtlet
            self.map = L.map(self.mapWidget)
            self.map.setView([47.7982, 13.0528], 6)
            L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(self.map)
            self.marker = L.marker([12.934056, 77.610029])
            self.marker.bindPopup('Test')
            self.markers = []
            self.markers.append(self.marker)
            self.map.addLayer(self.marker)
            self.show()

        def MapUpdate(self, lat, lon, ssid):
            #self.map = L.map(self.mapWidget)
            #self.map.setView([lon, lat], 6)
            #L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png').addTo(self.map)
            for marker2 in self.markers:
                self.map.removeLayer(marker2)
            marker1 = L.marker([lat, lon])
            marker1.bindPopup(ssid)
            self.map.addLayer(marker1)
            self.markers.append(marker1)
            #self.show()


    widget = MapWindow()

    grid.addWidget(widget, 0, 2, -1, 8)


    #grid.addWidget(Color('yellow'), 3, 4)


    #grid.addWidget(Color('blue'), 0, 2)


    #grid.addWidget(lbPlaceholder, 0, 6)


    #grid.addWidget(Color('purple'), 2, 2, 1, 2)



    #grid.setColumnStretch(2, 2)

 


    win.setLayout(grid)


    win.setWindowTitle("Probe Request Locator")


    #win.setGeometry(50, 50, 200, 200)


    win.showMaximized()

 


    sys.exit(app.exec_())

 

screen = window()

screen.showmox


