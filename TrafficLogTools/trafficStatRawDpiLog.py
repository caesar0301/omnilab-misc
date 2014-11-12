#!/usr/bin/env python
# Script to have a breakdown of NDPI output
# The output data can be used by R to plot.
# 
# This script obtains the statistics about traffic on link on protocal map.
# Each line in the output file gives traffic breakdown about each protocal
# with PROTOCAL NAME, FLOW COUNT, PACKET COUNT, BYTES COUNT.
#

__author__ =  'chenxm'
__email__ = 'chenxm35@gmail.com'


## We modify the gzip only to disable CRC check
import os
import sys
from glob import glob
from datetime import datetime

import pytz
import omnipy.utils.gzip_mod as gzip_mod

if len(sys.argv) != 2:
    print("Usage: program <dpi_out_folder>")
    exit(-1)
else:
    DPI_FOLDER = sys.argv[1]


class Statistics(object):
    def __init__(self):
        self.l4protos = {}  # {l4proto_name: set(subprotos)}
        self.data = {}      # {"subproto_name": [flows, packets, bytes]}

    def __str__(self):
        l4protos_list = self.l4protos.items()
        l4protos_list.sort(None, key=lambda x: x[0])
        s = ""
        for l4proto in l4protos_list:
            l4 = l4proto[0]
            subprotos = list(l4proto[1])
            subprotos.sort()
            for subproto in subprotos:
                data = self.data[subproto]
                s += '%20s  %15d  %15d  %15d\n' % (l4+':'+subproto, data[0], data[1], data[2])
        return s
         

def extract_datetime(auto_folder="20130503-2100.dpi.out"):
    datestr = auto_folder.rsplit('.')[0]
    dateobj = datetime.strptime(datestr, "%Y%m%d-%H%M")
    dateobj.replace(tzinfo = pytz.timezone('Asia/Shanghai'))
    return dateobj


def open_file(filename):
    parts = os.path.basename(filename).split('.')
    try:
        assert parts[-1] == 'gz'
        fh = gzip_mod.GzipFile(mode='rb', filename = filename)
    except:
        fh = open(filename, 'rb')
    return fh


def write_statistics(collection_item):
    """
    Each line: ProtocalName, Flow, Packets, Bytes
    """
    fos = open('dpi_stat.txt', 'ab')
    timestamp = "{0:%Y}-{0:%m}-{0:%d}-{0:%H}".format(collection_item[0])
    stat = collection_item[2]
    l4protos_list = stat.l4protos.items()
    l4protos_list.sort(None, key=lambda x: x[0])
    for l4proto in l4protos_list:
        l4 = l4proto[0]
        subprotos = list(l4proto[1])
        subprotos.sort()
        for subproto in subprotos:
            data = stat.data[subproto]
            fos.write("%s\t%s\t%d\t%d\t%d\n" % (timestamp, l4+":"+subproto, data[0], data[1], data[2]))
    fos.close()


## MAIN
collections = []    # [(datetime, pathname, statistics)]

for each_hour in glob(os.path.join(DPI_FOLDER, "*.out*")):
    period = extract_datetime(os.path.basename(each_hour))
    period = period.replace(minute = 0, second = 0)
    collections.append((period, each_hour, Statistics()))
collections.sort(None, key=lambda x: x[0])

print("Find %d files..." % len(collections))

i = 0
for item in collections:
    period = item[0]
    filepath = item[1]
    statistics = item[2]

    print "Processing %s" % str(period)
    print filepath
    fh = open_file(filepath)
    for line in fh:
        line = line.strip('\r \n')
        if len(line) == 0:
            continue
            
        params = line.split(' ')
        if len(params) < 9:
            continue
        try:
            int(params[-1])     # skip first line
        except:
            continue
        
        try:
            l4proto = params[5]
            subproto = params[6].split('/')[1]
            packets = int(params[7])
            tbytes = int(params[8])
        except:
            continue
        
        try:
            statistics.l4protos[l4proto].add(subproto)
        except KeyError:
            statistics.l4protos[l4proto] = set([subproto])
            
        try:
            statistics.data[subproto]
        except KeyError:
            statistics.data[subproto] = [0, 0, 0]
        statistics.data[subproto][0] += 1   # flow
        statistics.data[subproto][1] += packets
        statistics.data[subproto][2] += tbytes
            
    fh.close()

    print statistics
    write_statistics(item)
