from scapy.all import *
from json2table import convert
 
import requests
import json
import sys

# SOURCE: https://laptrinhx.com/building-a-wifi-spots-map-of-networks-around-you-with-wigle-and-python-2416726908/
# IMPORTING REQUIRED LIBRARIES:
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd
from pandas.io.json import json_normalize
import matplotlib.pyplot as plt
import geoplotlib as gp

reload(sys)
sys.setdefaultencoding('utf8')

# using API to checkout vendors by MAC
url = 'http://macvendors.co/api/%s'

# using API from wigle
url2 = 'https://api.wigle.net/api/v2/network/search'

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
	  
	  r2 = requests.get(url2, {'ssid':p.info, 'country':'AT'}, auth=('AID0c03e6a1fdff1332213ca04110bf6cb8', '6f7ae03341051392258941eda733365c'))
          
	  json_object = {"key" : "value"}
	  build_direction = "LEFT_TO_RIGHT"
          table_attributes = {"style" : "width:100%"}
          html = convert (r2.json(), build_direction=build_direction, table_attributes=table_attributes)
	  
          details = r2.json()
	  print(detail)
		
	  # SOURCE: https://laptrinhx.com/building-a-wifi-spots-map-of-networks-around-you-with-wigle-and-python-2416726908/	
          # EXTRACTING 'RESULTS' AS A PANDAS DATAFRAME TO WORK WITH:
          df = json_normalize(details['results'])
	
	  # SOURCE: https://laptrinhx.com/building-a-wifi-spots-map-of-networks-around-you-with-wigle-and-python-2416726908/
          # RENAMING COLUMNS FOR GEOPLOTLIB:
          df = df.rename(columns={'trilat': 'lat', 'trilong': 'lon'})
          cols = list(df.columns) 
          
	  # SOURCE: https://laptrinhx.com/building-a-wifi-spots-map-of-networks-around-you-with-wigle-and-python-2416726908/	
          # PREVIEWING AVAILABLE INFORMATION:
          print("Result obtained has {df.shape[0]} rows and {df.shape[1]} columns in it. \n\nThe list of columns include {cols}")

          print(df)
	  
	  # SOURCE: https://laptrinhx.com/building-a-wifi-spots-map-of-networks-around-you-with-wigle-and-python-2416726908/
          # GENERATING WIFI SPOTS MAP OF NETWORKS:
          gp.dot(df)
          gp.show()


scapy.all.sniff(iface=sys.argv[1],prn=search_prob)
