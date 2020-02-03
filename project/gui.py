import sys
from queue import Queue
from threading import RLock
from project.map import *
from project.datahandler import *
from project.sniffer import *
from project.wigle import *
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

vendor_for_mac = dict()
macs_per_ssid = dict()
ssids_per_mac = dict()


def window():
    app = QApplication(sys.argv)
    win = QWidget()

    btnStart = QPushButton('Start')
    btnStart.setToolTip('Start scanning for probe requests.')

    btnStop = QPushButton('Stop')
    btnStop.setToolTip('Stop scanning for probe requests.')

    drpdMenu = QComboBox()
    drpdMenu.addItem("MACs per SSID")
    drpdMenu.addItem("SSIDs per MAC")
    drpdMenu.setToolTip('group results by...')

    treeview = QTreeView()
    treeview.setAlternatingRowColors(True)
    model = QStandardItemModel(0, 1)
    model.setHeaderData(0, Qt.Horizontal, "SSIDs")
    rootNode = model.invisibleRootItem()
    treeview.setModel(model)

    btnWigle = QPushButton('SSID lookup')
    btnWigle.setToolTip('Check WiGLE database for selected SSID.')

    map = MapWindow()

    btnRemoveMarkers = QPushButton('Remove markers')
    btnRemoveMarkers.setToolTip('Remove all displayed location markers.')

    queue = Queue()
    lock = RLock()
    datahandler = DataHandler(queue, lock, drpdMenu, rootNode, vendor_for_mac, macs_per_ssid, ssids_per_mac)
    sniffer = Sniffer(queue, lock)

    def start_scan():
        datahandler.start()
        sniffer.start()

    def stop_scan():
        sniffer.join()
        datahandler.join()

    def drpd_changed():
        # remove Entries in List
        model.removeRows(0, model.rowCount())

        # select MACs per SSID as Data Store
        if drpdMenu.currentIndex() == 0:
            model.setHeaderData(0, Qt.Horizontal, "SSIDs")
            data_store = macs_per_ssid

        # select SSIDs per MAC as Data Store
        elif drpdMenu.currentIndex() == 1:
            model.setHeaderData(0, Qt.Horizontal, "MACs")
            data_store = ssids_per_mac

        # update List
        # insert Keys as Items
        for key in data_store.keys():
            if drpdMenu.currentIndex() == 0:
                new_item = QStandardItem(key)
            elif drpdMenu.currentIndex() == 1:
                new_item = QStandardItem(key + " - " + vendor_for_mac[key])
            new_item.setEditable(False)
            entries = data_store[key]

            # insert corresponding Entries as Child Items
            for entry in entries:
                if drpdMenu.currentIndex() == 0:
                    new_child_item = QStandardItem(entry + " - " + vendor_for_mac[entry])
                elif drpdMenu.currentIndex() == 1:
                    new_child_item = QStandardItem(entry)
                new_child_item.setEditable(False)
                new_item.appendRow(new_child_item)

            rootNode.appendRow(new_item)
            resize()

    def resize():
        treeview.resizeColumnToContents(0)

    def remove_markers():
        map.remove_markers()

    def ssid_lookup():
        if rootNode.rowCount() == 0:
            msgBox = QMessageBox()
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setWindowTitle("Alert")
            msgBox.setText("Please select a SSID for database lookup.")
            return msgBox.exec()
        for ix in treeview.selectedIndexes():
            parent = ix.parent()
            parent_t = parent.data()
            text = ix.data()
        if drpdMenu.currentIndex() == 0:
            if parent_t is None:
                ssid = text
            else:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setWindowTitle("Alert")
                msgBox.setText("Please select a SSID for database lookup.")
                return msgBox.exec()

        elif drpdMenu.currentIndex() == 1:
            if parent_t is None:
                msgBox = QMessageBox()
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setWindowTitle("Alert")
                msgBox.setText("Please select a SSID for database lookup.")
                return msgBox.exec()
            else:
                ssid = text

        wigle = Wigle(ssid, map)
        wigle.start()

    btnStart.clicked.connect(start_scan)
    btnStop.clicked.connect(stop_scan)
    drpdMenu.currentIndexChanged.connect(drpd_changed)
    treeview.expanded.connect(resize)
    treeview.collapsed.connect(resize)
    btnRemoveMarkers.clicked.connect(remove_markers)
    btnWigle.clicked.connect(ssid_lookup)

    grid = QGridLayout()
    grid.addWidget(btnStart, 0, 0)
    grid.addWidget(btnStop, 0, 1)
    grid.addWidget(drpdMenu, 1, 0)
    grid.addWidget(treeview, 3, 0, 4, 2)
    grid.addWidget(btnWigle, 8, 1)
    grid.addWidget(map, 0, 3, 0, 8)
    grid.addWidget(btnRemoveMarkers, 8, 0)

    win.setLayout(grid)
    win.setWindowTitle("Probe Request Locator")
    win.showMaximized()

    sys.exit(app.exec_())


screen = window()
screen.showmox


