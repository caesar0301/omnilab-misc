#!/usr/bin/env python
# Read the user_touch_screen file
# Read the processed_events file

import os
import sys
import glob
import logging

import dpkt

#logger
# logging.basicConfig(
# filename=os.path.basename(sys.argv[0]).rsplit('.',1)[0]+'.log',
# level=logging.DEBUG)

def print_usage():
    print("Usage: python prog_name <omniperf_trace>")

if len(sys.argv) < 2:
    print_usage()
    sys.exit(-1)

input_folder = sys.argv[1]

ts = os.path.join(input_folder, 'user_touch_screen')
evt = os.path.join(input_folder, 'processed_events')

if os.path.exists(ts):
    print("Find user_touch_screen ... ")

    output = os.path.join(input_folder, 'userclicks.out')
    #logging.info("output %s" % output)
    of = open(output, 'wb')
    of.write('time\tscreen_x\tscreen_y\n')
    for line in open(ts):
        line = line.strip('\t\r\n ')
        if len(line)==0 or line[0]=='#':
            continue
        parts = line.split(' ')
        if len(parts) < 3:
            #logging.warn('Abnormal content line: ' + line)
            continue
        millisec = parts[1]
        position = parts[2].split(':')
        
        of.write('%s\t%s\t%s\n' % (millisec, position[0], position[1]))
    of.close()

if os.path.exists(evt):
    print("Find processed_events ... ")

    output = os.path.join(input_folder, 'userclicks2.out')
    #logging.info("output %s" % output)
    of = open(output, 'wb')
    of.write('time\tscreen_x\tscreen_y\n')

    start_ts = None
    prev_ts = None
    clicks = 0
    for line in open(evt):
        line = line.strip('\t\r\n ')
        if len(line)==0 or line[0]=='#':
            continue
        parts = line.split(' ')
        if len(parts) < 3:
            #logging.warn('Abnormal content line: ' + line)
            continue

        ts = float(parts[0])
        dev = parts[1]
        action = parts[2]
        if dev != 'screen': # detect "screen *" string
            continue

        if start_ts is None:
            # initialization
            start_ts = ts
            prev_ts = ts
            continue
        
        if ts - prev_ts < 1: # one second
            prev_ts = ts
        else:
            clicks += 1
            of.write('%s\t%d\t%d\n' % (start_ts, -1, -1))
            start_ts = ts
            prev_ts = ts

    of.close()

    print "clicks", clicks