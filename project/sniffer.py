#authors: Leonhard Jauch, Michael Kaltenbrunner, Tobias Pfeiffer
#university of applied sciences Salzburg, ITS-B2017

from scapy.all import *
from threading import Thread, Event

# src: https://www.pythoncentral.io/how-to-create-a-thread-in-python/
# src: https://blog.skyplabs.net/2018/03/01/python-sniffing-inside-a-thread-with-scapy/
# Use scapy in thread
class Sniffer(Thread):
    def __init__(self, iface, queue):
        super().__init__()
        self.daemon = True
        self.iface = iface
        self.queue = queue
        self.stop_sniffer = Event()

    def run(self):
        while True:
            try:
                sniff(iface=self.iface, prn=self.search_probe, stop_filter=self.should_stop_sniffer)
            except:
                continue

    def join(self, timeout=None):
        self.stop_sniffer.set()
        super().join(timeout)

    def should_stop_sniffer(self, p):
        return self.stop_sniffer.isSet()

    def search_probe(self, p):
        if p.type == 0:
            if p.subtype == 4:
                if p.info != b'':
                    mac = p.addr2
                    ssid = p.info
                    power = p.dBm_AntSignal
                    self.queue.put([mac, ssid, power])
