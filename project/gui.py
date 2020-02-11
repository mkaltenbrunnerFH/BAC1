#authors: Leonhard Jauch, Michael Kaltenbrunner, Tobias Pfeiffer
#university of applied sciences Salzburg, ITS-B2017

import sys
import os
from queue import Queue
from configparser import ConfigParser
from threading import Lock
from mapwindow import *
from datahandler import *
from sniffer import *
from wigle import *
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot, QModelIndex

Config = ConfigParser()
Config.read('iface.conf')
try:
    name = Config.get('iface', 'name')
    monname = Config.get('iface', 'monname')
except:
    raise ValueError('Please enter your API key into the wigle.conf file. See https://api.wigle.net')

# src: https://stackoverflow.com/questions/42434198/pyqt-write-inherit-from-qwidget
# Class for Graphical User Interface
class GUI(QWidget):

    # https://www.riverbankcomputing.com/static/Docs/PyQt5/signals_slots.html
    # Signals are used to ensure that the main thread is the only thread to access the GUI
    update_list_view = pyqtSignal(str, str, str, int, bool, bool)
    renew_probe = pyqtSignal(str, str, str, int)
    map_update = pyqtSignal(str, int, list)
    no_results = pyqtSignal(str)

    # initialize GUI
    def __init__(self, parent=None):

        super(GUI, self).__init__(parent)
        self.setWindowTitle("Probe Request Locator")
        self.init_ui()
        self.init_dicts()
        self.init_threads()
        self.showMaximized()

    # initializes elements that are shown in GUI
    def init_ui(self):

        # src: https://www.riverbankcomputing.com/static/Docs/PyQt5/
        lblScan = QLabel("Scan in progress...")
        self.drpdMenu = QComboBox()
        self.drpdMenu.setToolTip('group results by...')
        self.drpdMenu.addItem("MACs per SSID")
        self.drpdMenu.addItem("SSIDs per MAC")

        btnExpand = QPushButton('Expand all')
        btnExpand.setToolTip('Expand all items in list.')
        btnCollapse = QPushButton('Collapse all')
        btnCollapse.setToolTip('Collapse all items in list')

        #src: https://joekuan.wordpress.com/2016/02/11/pyqt-how-to-hide-top-level-nodes-in-tree-view/
        self.trvList = QTreeView()
        self.trvList.setAlternatingRowColors(True)
        self.model = QStandardItemModel(0, 1)
        self.model.setHeaderData(0, Qt.Horizontal, "SSIDs")
        self.rootNode = self.model.invisibleRootItem()
        self.trvList.setModel(self.model)

        self.btnWigle = QPushButton('SSID lookup')
        self.btnWigle.setToolTip('Check WiGLE database for selected SSID.')
        btnRemoveMarkers = QPushButton('Remove markers')
        btnRemoveMarkers.setToolTip('Remove all displayed location markers.')

        self.resultCounter = 0
        self.lblLastCount = QLabel()
        self.lblLastCount.setAlignment(Qt.AlignCenter)
        self.lblTotalCount = QLabel()
        self.lblTotalCount.setAlignment(Qt.AlignCenter)

        self.map = MapWindow()

        # connections to functions
        self.drpdMenu.currentIndexChanged.connect(self.drpd_changed)
        btnExpand.clicked.connect(self.expand)
        btnCollapse.clicked.connect(self.collapse)
        self.trvList.expanded.connect(self.resize)
        self.trvList.collapsed.connect(self.resize)
        self.btnWigle.clicked.connect(self.ssid_lookup)
        btnRemoveMarkers.clicked.connect(self.remove_markers)

        # src: https://pythonspot.com/pyqt5-grid-layout/
        # grid layout
        grid = QGridLayout()
        grid.addWidget(lblScan, 0,0)
        grid.addWidget(self.drpdMenu, 0, 1)
        grid.addWidget(btnExpand, 1, 0)
        grid.addWidget(btnCollapse, 1, 1)
        grid.addWidget(self.trvList, 2, 0, 5, 2)
        grid.addWidget(self.btnWigle, 7, 1)
        grid.addWidget(self.map, 0, 3, 0, 8)
        grid.addWidget(btnRemoveMarkers, 7, 0)
        grid.addWidget(self.lblLastCount, 8, 0, 1, 2)
        grid.addWidget(self.lblTotalCount, 9, 0, 1, 2)
        self.setLayout(grid)

    # initializes dictionaries used to store probe data
    def init_dicts(self):

        self.vendor_for_mac = dict()
        self.macs_per_ssid = dict()
        self.ssids_per_mac = dict()

    # initializes and starts threads and their components
    def init_threads(self):

        # WiGLE thread
        self.lookups = Queue()
        wigle = Wigle(self.lookups, self.map_update, self.no_results)
        self.no_results.connect(self.handle_no_results)
        self.map_update.connect(self.handle_map_update)

        # DataHandler tread
        probe_buffer = Queue()
        self.dict_lock = Lock()
        datahandler = DataHandler(probe_buffer, self.dict_lock, self.update_list_view, self.renew_probe,
                                  self.vendor_for_mac, self.macs_per_ssid, self.ssids_per_mac)
        self.update_list_view.connect(self.handle_update_list_view)
        self.renew_probe.connect(self.handle_renew_probe)

        # Sniffer thread
        sniffer = Sniffer(monname, probe_buffer)

        wigle.start()
        datahandler.start()
        sniffer.start()

    # function to execute when drop-down-menu option has changed
    def drpd_changed(self):

        # remove current entries in list
        self.model.removeRows(0, self.model.rowCount())

        # select MACs per SSID as Data Store
        if self.drpdMenu.currentIndex() == 0:
            self.model.setHeaderData(0, Qt.Horizontal, "SSIDs")
            self.insert_items(self.macs_per_ssid, 0)

        # select SSIDs per MAC as Data Store
        elif self.drpdMenu.currentIndex() == 1:
            self.model.setHeaderData(0, Qt.Horizontal, "MACs")
            self.insert_items(self.ssids_per_mac, 1)

    # creates a child item for the parent and inserts the passed information
    def create_child_item(self, parent, subkey, timestamp, power, option):

        if option == 0:
            child_item = QStandardItem(subkey + " - " + self.vendor_for_mac[subkey])
        if option == 1:
            child_item = QStandardItem(subkey)
        child_item.setEditable(False)
        ts = QStandardItem("Timestamp: %s" % timestamp)
        ts.setEditable(False)
        pw = QStandardItem("Power at timestamp: %d dBm" % power)
        pw.setEditable(False)
        child_item.appendRow(ts)
        child_item.appendRow(pw)
        parent.appendRow(child_item)

    # insertion of items in list
    def insert_items(self, datastore, option):

        # lock dictionaries
        self.dict_lock.acquire()

        # iterate through the passed dictionary and insert all items
        for key in datastore:
            if option == 0:
                item = QStandardItem(key)
            elif option == 1:
                item = QStandardItem(key + " - " + self.vendor_for_mac[key])
            item.setEditable(False)
            for subkey in datastore[key]:
                self.create_child_item(item, subkey, datastore[key][subkey]['timestamp'], datastore[key][subkey]['power'], option)
            self.rootNode.appendRow(item)

        # release the lock again
        self.dict_lock.release()
        self.resize()

    # expand all items in list
    def expand(self):

        self.trvList.expandAll()
        self.resize()

    # collapse all items in list
    def collapse(self):

        self.trvList.collapseAll()
        self.resize()

    # automatically adjust column to longest entry
    def resize(self):

        self.trvList.resizeColumnToContents(0)

    # remove shown markers on the map
    def remove_markers(self):

        self.map.remove_markers()
        if self.resultCounter > 0:
            self.resultCounter = 0
            self.lblTotalCount.setText("No results shown in map")

    # get selected ssid and give it to the WiGLE thread
    def ssid_lookup(self):

        # cancel if no ssid is selected
        if self.rootNode.rowCount() == 0:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setWindowTitle("Alert")
            msgBox.setText("Please select a SSID for database lookup.")
            return msgBox.exec()

        # src: https://stackoverflow.com/questions/47621042/get-the-text-and-index-of-the-current-selected-qtreeview-item
        # get selected item and check if it a ssid
        for index in self.trvList.selectedIndexes():
            parent = index.parent()
            parent_text = parent.data()
            text = index.data()

        # if dropdown option is macs per ssid, then ssid must at highest hierarchical level, otherwise cancel
        if self.drpdMenu.currentIndex() == 0:
            if parent_text is None:
                ssid = text
            else:
                return self.show_alert()

        # if dropdown option is ssids per mac then ssid must be at second highest hierarchical level, otherwise cancel
        elif self.drpdMenu.currentIndex() == 1:
            if parent_text is None:
                return self.show_alert()

            elif index.parent().parent() == QModelIndex():
                ssid = text
            else:
                return self.show_alert()

        # add ssid to queue for WiGLE thread
        self.lookups.put(ssid)
        # disable button during API request
        self.btnWigle.setDisabled(True)
        self.btnWigle.setText("loading...")

    # show message box if no ssid is selected
    def show_alert(self):

        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Critical)
        msgBox.setWindowTitle("Alert")
        msgBox.setText("Please select a SSID for database lookup.")
        msgBox.exec()

    # function connected to signal 'update_list_view'
    @pyqtSlot(str, str, str, int, bool, bool)
    def handle_update_list_view(self, mac, ssid, timestamp, power, mac_existed, ssid_existed):

        # lock dictionaries
        self.dict_lock.acquire()

        # macs per ssid
        if self.drpdMenu.currentIndex() == 0:
            # insert new parent item in list and append child
            if not ssid_existed:
                item = QStandardItem(ssid)
                item.setEditable(False)
                self.create_child_item(item, mac, timestamp, power, 0)
                self.rootNode.appendRow(item)

            else:
                # get parent item and append child
                for i in range(self.rootNode.rowCount()):
                    item = self.rootNode.child(i)
                    if item.text() == ssid:
                        self.create_child_item(item, mac, timestamp, power, 0)

        # ssids per mac
        elif self.drpdMenu.currentIndex() == 1:
            # insert new parent item in list and append child
            if not mac_existed:
                item = QStandardItem(mac + " - " + self.vendor_for_mac[mac])
                item.setEditable(False)
                self.create_child_item(item, ssid, timestamp, power, 1)
                self.rootNode.appendRow(item)

            else:
                # get parent item and append child
                for i in range(self.rootNode.rowCount()):
                    item = self.rootNode.child(i)
                    if item.text() == (mac + " - " + self.vendor_for_mac[mac]):
                        self.create_child_item(item, ssid, timestamp, power, 1)

        # release the lock again
        self.dict_lock.release()

    # function connected to signal 'renew_probe'
    @pyqtSlot(str, str, str, int)
    def handle_renew_probe(self, mac, ssid, timestamp, power):

        # lock dictionaries
        self.dict_lock.acquire()

        if self.drpdMenu.currentIndex() == 0:
            key = ssid
            subkey = mac + " - " + self.vendor_for_mac[mac]

        elif self.drpdMenu.currentIndex() == 1:
            key = mac + " - " + self.vendor_for_mac[mac]
            subkey = ssid

        # find the correct probe and replace timestamp and power
        for i in range(self.rootNode.rowCount()):
            item = self.rootNode.child(i)
            if item.text() == key:
                for j in range(item.rowCount()):
                    child_item = item.child(j)
                    if child_item.text() == (subkey):
                        ts = child_item.child(0)
                        ts.setText("Timestamp: " + timestamp)
                        pw = child_item.child(1)
                        pw.setText("Power at timestamp: %d dBm" % power)

        # release the lock again
        self.dict_lock.release()

    # function connected to signal 'map_update'
    @pyqtSlot(str, int, list)
    def handle_map_update(self, ssid, resultCount, entries):

        # bounds are used to set the view after a API request that returned results
        bounds = list()
        for entry in entries:
            lat = entry['trilat']
            lon = entry['trilong']
            bounds.append([lat, lon])
            self.map.set_marker(lat, lon, ssid)

        self.map.fit(bounds)

        # set informative text in labels
        res = "result" if resultCount == 1 else "results"
        self.lblLastCount.setText("%d %s from last lookup" % (resultCount, res))
        self.resultCounter += resultCount
        res2 = "result" if self.resultCounter == 1 else "results"
        self.lblTotalCount.setText("%d %s shown in map" % (self.resultCounter, res2))

        # enable button again
        self.btnWigle.setEnabled(True)
        self.btnWigle.setText("SSID lookup")

    # function connected to signal 'no_results'
    @pyqtSlot(str)
    def handle_no_results(self, ssid):

        # set text in label and return a message box
        self.lblLastCount.setText("No results from last lookup")
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setWindowTitle("Information")
        msgBox.setText("No entry for SSID '%s' found in WiGLE database." % ssid)

        # enable button again
        self.btnWigle.setEnabled(True)
        self.btnWigle.setText("SSID lookup")
        return msgBox.exec()

    # function to execute when window closes
    def closeEvent(self, event):
        os.system("sudo airmon-ng stop %s" % monname)


if __name__ == '__main__':

    os.system("sudo airmon-ng start %s" % name)
    os.system("sudo ifconfig %s up" % monname)
    app = QApplication(sys.argv)
    ex = GUI()
    sys.exit(app.exec_())
