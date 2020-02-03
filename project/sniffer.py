from scapy.all import *
from threading import Thread, Event


class Sniffer(Thread):
    def __init__(self, queue, lock):
        super().__init__()
        self.daemon = True
        self.queue = queue
        self.lock = lock
        self.probe_data = set()
        self.stop_sniffer = Event()

    def run(self):
        sniff(iface="wlan0mon", prn=self.search_probe, stop_filter=self.should_stop_sniffer)

    def join(self, timeout=None):
        self.stop_sniffer.set()
        super().join(timeout)

    def should_stop_sniffer(self, p):
        return self.stop_sniffer.isSet()

    def search_probe(self, p):
        if p.type == 0 and p.subtype == 4 and p.info != b'':
            mac_and_ssid = (p.addr2, p.info)
            if mac_and_ssid not in self.probe_data:
                self.probe_data.add(mac_and_ssid)
                self.queue.put(mac_and_ssid)
