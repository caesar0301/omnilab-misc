#!/usr/bin/env python
#
# This script facilitates wifi sessions of wifilog-filter to mark allocated IP address
# to each session.
# The input can be a file or folder. If its the latter, multiple input files will be merged
# into a single output.
#
# INPUT:
# the output of wifilog filter.
#
# INPUT FORMAT:
# ec55f9c3c9f9    2013-09-29 00:37:40 2013-09-29 00:37:40 0   MLXY-3F-08
# 50ead62002f7    2013-09-29 06:16:12 2013-09-29 06:16:31 19  LXZL-4F-03
# 40f3088b77ff    2013-09-29 00:43:32 2013-09-29 00:43:48 23  MH-LXZL-2
# 40f3088b77ff    2013-09-29 00:43:38 IPAllocation    111.186.40.54
#
# OUTPUT FORMAT:
# c8aa2149fdc9 111.186.12.184 1367379815 GBL-1F-02 1367379839
# c8aa2149fdc9 111.186.12.184 1367379839 GBL-1F-05 1367380028
# c8aa2149fdc9 111.186.12.184 1367382893 GBL-2F-02 1367383921
# c8aa2149fdc9 111.186.12.184 1367400918 DEST-1F-02 1367401711
#
import sys

from PyOmniMisc.wifi.movement import ApEntry, LocationDB

def print_usage():
    print("Usage: python parseWifiSessions.py <inputpath/file> <outputfile>")

if len(sys.argv) < 3:
    print_usage()
    sys.exit(-1)
else:
    inputpath = sys.argv[1]
    outputfile = sys.argv[2]

ldb = LocationDB(inputpath)

print("Dumping sessions with IP addr .. ")
ofile = open(outputfile, 'wb')
for mac, ap_entries in ldb.getMacApDatabase().items():
    ap_entries.sort(key=lambda x:x.start, reverse=False)
    for ap_entry in ap_entries:
        ap_info = '{0} {1} {2}'.format(int(ap_entry.start), ap_entry.name, int(ap_entry.end))
        ofile.write("%s %s %s\n" % (mac, ldb.getIpByMac(mac, ap_entry.start), ap_info))
ofile.close()