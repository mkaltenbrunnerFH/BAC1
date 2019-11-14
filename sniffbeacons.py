#!/usr/bin/env python

from scapy.all import Dot11, sniff
                       

ap_list = []

def PacketHandler(packet) :
    if packet.haslayer(Dot11) :
        if packet.type == 0 and packet.subtype == 8:
            if packet.addr2 not in ap_list:
                ap_list.append(packet.addr2)
                print("Access Point MAC: %s with SSID: %s " %(packet.addr2, packet.info))


sniff(iface="wlp2s0", prn = PacketHandler)
