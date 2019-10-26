

import sys, scapy.all

 

scapy.all.conf.iface = sys.argv[1]

 

data = set()

 

def update(p):


    try:


        if p.subtype == 4:


            if p.info != b'':

	        h = (p.info, p.addr2)

               # h = (p.info, p.addr2), p.dBm_AntSignal)

                if not h in data:            


                    print(h)


                    data.add(h)


    except AttributeError:


        pass

    

pkts = scapy.all.sniff(prn=update)


