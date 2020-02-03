from PyQt5.QtWidgets import QWidget, QVBoxLayout
from pyqtlet import MapWidget, L


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
        self.markers = []
        self.show()

    def remove_markers(self):
        for marker in self.markers:
            self.map.removeLayer(marker)

    def set_marker(self, lat, lon, ssid):
        # self.map.flyTo([lat, lon], 8)
        marker = L.marker([lat, lon])
        marker.bindPopup(ssid)
        self.map.addLayer(marker)
        self.markers.append(marker)