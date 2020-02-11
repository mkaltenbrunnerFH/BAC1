#authors: Leonhard Jauch, Michael Kaltenbrunner, Tobias Pfeiffer
#university of applied sciences Salzburg, ITS-B2017

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from pyqtlet import MapWidget, L

# src: https://pyqtlet.readthedocs.io/en/latest/getting-started.html
# src: https://github.com/skylarkdrones/pyqtlet
# MapWindow widget for GUI
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
        L.tileLayer('http://{s}.tile.openstreetmap.de/{z}/{x}/{y}.png').addTo(self.map)
        self.markers = list()

    def fit(self, bounds):
        self.map.setMaxZoom(10)
        self.map.fitBounds(bounds)
        self.map.setMaxZoom(18)

    def remove_markers(self):
        for marker in self.markers:
            self.map.removeLayer(marker)

    def set_marker(self, lat, lon, ssid):
        marker = L.marker([lat, lon])
        marker.bindPopup(ssid)
        self.map.addLayer(marker)
        self.markers.append(marker)
