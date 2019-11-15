from scapy.all import *
 
import requests
import json
import sys

# using API to checkout vendors by MAC
url = 'http://macvendors.co/api/%s'

probe_data = set()
beacon_data = set()

def search_prob(p):
    if (p.type == 0) and\
    (p.subtype == 4) and\
    (p.info != b''):
        mac_and_ssid = (p.addr2,p.info)
        if (mac_and_ssid not in probe_data):
          r = requests.get(url % p.addr2)
          req = json.loads(r.content)
          print("PrbReq, SSID = %s, Src = %s, Vendor = %s" %(p.info, p.addr2, req['result']['company']))
          probe_data.add(mac_and_ssid)
    elif (p.type == 0) and\
    (p.subtype == 8):
        beacon = (p.addr2, p.info)
        if (beacon not in beacon_data):
          r = requests.get(url % p.addr2)
          req = json.loads(r.content)
          print("Beacon, SSID = %s, Src = %s, Vendor = %s" %(p.info, p.addr2, req['result']['company']))
          beacon_data.add(beacon)

scapy.all.sniff(iface=sys.argv[1],prn=search_prob)
