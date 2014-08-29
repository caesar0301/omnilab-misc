#!/usr/bin/env python
import os
import sys
import glob
import logging
import stat
from subprocess import *

import nids
import dpkt # inspect deep packet content

#logger
#logging.basicConfig(filename=os.path.basename(sys.argv[0]).rsplit('.',1)[0]+'.log',level=logging.DEBUG)


def print_usage():
    print("Usage: python flowBurst.py <omniperf_trace>")


if len(sys.argv) < 2:
    print_usage()
    sys.exit(-1)

input_folder = sys.argv[1]
output = os.path.join(input_folder, 'flow_times.out')
try:
    os.remove(output)
except OSError:
    pass
#logging.info("output %s" % output)

of = open(output, 'wb')
of.write('time\tduration\tpackets\tstate\n')
of.close()

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

    cmd = "python flow_burst_single.py {0} >> {1}".format(pcap_file, output)
    #logging.debug(cmd)
    Popen(cmd, shell=True, stdout=PIPE).communicate()