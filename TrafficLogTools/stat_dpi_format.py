#!/usr/bin/env python
# Caculate total traffic volumes of TOP-N protocols besides the
# Unkown signature.
#
# Output:
# The first colume indicates the date/hour time.
# The last colume shows unknow protocol breakdown.
# The others indicate traffic breakdown of TOP-N protocols.
# Each colume takes three counters: FLOWS, PACKETS, and BYTES.
#
__author__ =  'chenxm'
__email__ = 'chenxm35@gmail.com'

import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Post processing of DPI statistics.")
    parser.add_argument("-4", action="store_true", dest='if_extract_layer4', help="The flag that indicates if layer 4 protocols are inspected.")
    parser.add_argument("inputfile", type=argparse.FileType('r'), help="The input DPI statistics file.")
    parser.add_argument("outputfile", type=argparse.FileType('w'), help="The output formatted statistics about each protocol.")
    args = parser.parse_args()
    inputfile = args.inputfile
    outputfile = args.outputfile

    stat_hours = [] # (hour, stat)
    detected_protos = set()
    for line in inputfile:
        parts = line.strip(' \r\n').split('\t')
        this_hour = parts[0]
        proto_stat = {}     # store breakdown: {"protoname": [flows, packets, bytes]}
        for part in parts[1:]:
            if part.strip(' \t') == "":
                continue
            inparts = part.rsplit(':')
            l4_proto = inparts[0]
            l7_proto = inparts[1]
            flows, packets, bytes = inparts[2].split(',')
            proto_name = l7_proto if l7_proto.lower() != 'unknown' else (l4_proto+'-'+l7_proto)
            if args.if_extract_layer4:
                proto_name = l4_proto
            if proto_name not in detected_protos:
                detected_protos.add(proto_name)
            if proto_name not in proto_stat:
                proto_stat[proto_name] = [0,0,0]
            proto_stat[proto_name][0] += int(flows)
            proto_stat[proto_name][1] += int(packets)
            proto_stat[proto_name][2] += int(bytes)
        stat_hours.append((this_hour, proto_stat))
        
    detected_protos_list = list(detected_protos)
    detected_protos_list.sort()
    outputfile.write("time %s" % (' '.join(detected_protos_list)))
    outputfile.close()
    
    # for test
    culstat = {} # {"protoname": [flows, packets, bytes]}
    for hour in stat_hours:
        proto_stat = hour[1]
        for key in proto_stat:
            if key not in culstat:
                culstat[key] = proto_stat[key]
            else:
                culstat[key][0] += proto_stat[key][0]
                culstat[key][1] += proto_stat[key][1]
                culstat[key][2] += proto_stat[key][2]
    proto_list = culstat.items()
    proto_list.sort(key=lambda x: x[1][2], reverse=True)    # sorted by bytes
    for proto in proto_list:
        print proto[0], proto[1][0], proto[1][1], proto[1][2]

