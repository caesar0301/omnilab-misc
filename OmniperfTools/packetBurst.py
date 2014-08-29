#!/usr/bin/env python
import os
import sys
import glob
import logging

import dpkt

#logger
#logging.basicConfig(filename=os.path.basename(sys.argv[0]).rsplit('.',1)[0]+'.log',level=logging.DEBUG)

def print_usage():
    print("Usage: python prog_name <omniperf_trace>")

def is_tcp_pkt(buf):
    is_tcp = False
    try:
        eth = dpkt.ethernet.Ethernet(buf)
        if eth.type == dpkt.ethernet.ETH_TYPE_IP:
            ip = eth.ip
            if ip.p == dpkt.ip.IP_PROTO_TCP:
                is_tcp = True
        else:
            # Try Raw IP
            ip = dpkt.ip.IP(buf)
            if ip.p == dpkt.ip.IP_PROTO_TCP:
                is_tcp = True
    except dpkt.NeedData, e:
        print "dpkt needdata", e
    except AttributeError, e:
        print "eth data error", e
    except Exception, e:
        #print "misc error", e
        pass

    return is_tcp

if len(sys.argv) < 2:
    print_usage()
    sys.exit(-1)

input_folder = sys.argv[1]
output = os.path.join(input_folder, 'packet_times.out')
#logging.info("output %s" % output)

of = open(output, 'wb')
of.write('time\tis_burst_500\n')

previous_packet_ts = None
tcp_cnt = 0

pcap_files = glob.glob(os.path.join(input_folder, 'traffic*.cap'))
# sort traces by creation time
# using creating time? No
# pcap_files.sort(cmp=lambda x,y: cmp(x,y), key=lambda x: os.stat(x)[stat.ST_CTIME], reverse=False)
# using order number?
def getTraceNum(trace):
    bname = os.path.basename(trace).split('.',1)
    num = bname[0][len('traffic') : ]
    num = 0 if num == '' else int(num)
    return num
pcap_files.sort(lambda x,y: cmp(getTraceNum(x),getTraceNum(y)), None, False)

for pcap_file in pcap_files:
    try:
        print(pcap_file)
        for ts, buf in dpkt.pcap.Reader(open(pcap_file, 'rb')):
            is_tcp = is_tcp_pkt(buf)
            #print is_tcp
            if not is_tcp:
                continue
            tcp_cnt += 1
            if previous_packet_ts is not None:
                delta = ts - previous_packet_ts
                of.write('%.3f\t%d\n' % (ts, 1 if delta < 0.5 else 0))
            else:
                of.write('%.3f\t%d\n' % (ts, 0))
            previous_packet_ts = ts
    except dpkt.NeedData:
        continue

of.close()

print "tcp pkts ", tcp_cnt