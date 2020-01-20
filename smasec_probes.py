from scapy.all import *
from json2table import convert

import requests
import json
import sys
import importlib

# SOURCE: https://laptrinhx.com/building-a-wifi-spots-map-of-networks-around-you-with-wigle-and-python-2416726908/
# IMPORTING REQUIRED LIBRARIES:
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from pandas.io.json import json_normalize
import matplotlib.pyplot as plt
import geoplotlib as gp

# importlib.reload(sys)
# sys.setdefaultencoding('utf8')

# using API to checkout vendors by MAC
url = 'http://macvendors.co/api/%s'

# using API from wigle
url2 = 'https://api.wigle.net/api/v2/network/search'

probe_data = set()


def search_prob(p):
    if p.type == 0 and \
            p.subtype == 4 and \
            p.info != b'':
        mac_and_ssid = (p.addr2, p.info)
        if not mac_and_ssid in probe_data:
            r = requests.get(url % p.addr2)
            req = json.loads(r.content)
            try:
                vendor = req['result']['company']
            except KeyError:
                vendor = "Unknown"

            print("SSID = %s, Src = %s, Vendor = %s" % (p.info, p.addr2, vendor))

            probe_data.add(mac_and_ssid)

            r2 = requests.get(url2, {'ssid': p.info, 'country': 'AT'},
                              auth=('AID0c03e6a1fdff1332213ca04110bf6cb8', '6f7ae03341051392258941eda733365c'))

            #json_object = {"key": "value"}
            #build_direction = "LEFT_TO_RIGHT"
            #table_attributes = {"style": "width:100%"}
            #html = convert(r2.json(), build_direction=build_direction, table_attributes=table_attributes)

            detail = r2.json()
            #print(detail)
            if(detail['totalResults'] > 0):
                # SOURCE: https://laptrinhx.com/building-a-wifi-spots-map-of-networks-around-you-with-wigle-and-python-2416726908/
                # EXTRACTING 'RESULTS' AS A PANDAS DATAFRAME TO WORK WITH:
                df = json_normalize(detail['results'])

                # SOURCE: https://laptrinhx.com/building-a-wifi-spots-map-of-networks-around-you-with-wigle-and-python-2416726908/
                # RENAMING COLUMNS FOR GEOPLOTLIB:
                df = df.rename(columns={'trilat': 'lat', 'trilong': 'lon'})
                cols = list(df.columns)

                # SOURCE: https://laptrinhx.com/building-a-wifi-spots-map-of-networks-around-you-with-wigle-and-python-2416726908/
                # PREVIEWING AVAILABLE INFORMATION:
                print("Result obtained has {df.shape[0]} rows and {df.shape[1]} columns in it. \n\nThe list of columns include {cols}")

                #print(df)

                # SOURCE: https://laptrinhx.com/building-a-wifi-spots-map-of-networks-around-you-with-wigle-and-python-2416726908/
                # GEiNERATING WIFI SPOTS MAP OF NETWORKS:
                gp.dot(df)
                gp.show()
            else:
                print("No entry in Wigle for SSID %s" % p.info)



scapy.all.sniff(iface=sys.argv[1], prn=search_prob)
