#!/usr/bin/env python
# Extract http logs of traces
#
# Usage:
#     cd OmniperfTools
#     python exHttp.py trace_folder
#
import os
import sys
import glob
from subprocess import *

def print_usage():
    print("Usage: python exHttp.py <omniperf_trace>")


if len(sys.argv) < 2:
    print_usage()
    sys.exit(-1)

input_folder = sys.argv[1]
output = os.path.join(input_folder, 'http_logs')
try:
    os.remove(output)
except OSError:
    pass

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
    print(pcap_file)
    # call flow burst single file

    cmd = "../TrafficLogExtraction/offline/justniffer-run.sh -o {1} {0}".format(pcap_file, output)
    #logging.debug(cmd)
    Popen(cmd, shell=True, stdout=PIPE).communicate()