#!/usr/bin/env python
# Program to split pcap traces into client and 
# server sides in order to be used by TCPREPLY.
#
# If only the --client network is explicit, the packets with source IP belonging to the network 
# are classified as client while all the others are classified as the server side. It's the 
# same that only --server network is explicit.
# If the --client and --server are both explicit, the packets with source IP belonging to 
# the client AND destination IP belonging to the server are classified as client;
# the packets with reversed direction are classified as server side; and the left is ignored.
#
# by chenxm
# sites.google.com/site/xiamingch
# 2012-12

import pcapy    # http://oss.coresecurity.com/projects/pcapy.html
import ipaddr   # http://code.google.com/p/ipaddr-py/
import sys
import string
import time
import socket
import struct
import argparse
import re
import os

_PCAP_READER = None
_CLIENT_IP_FILTER =  []
_SERVER_IP_FILTER = []
_PACKET_DIRECTION_CLIENT = 0
_PACKET_DIRECTION_SERVER = 1
_OUT_CLIENT_FILE = 'client.pcap'
_OUT_SERVER_FILE = 'server.pcap'
_DUMPER_CLIENT = None
_DUMPER_SERVER = None

def decode_ip_packet(s):
  d={}
  d['source_address']=socket.inet_ntoa(s[12:16])
  d['destination_address']=socket.inet_ntoa(s[16:20])
  return d

def packet_direction(ip_d):
    src_addr = ip_d['source_address']
    dst_addr = ip_d['destination_address']
    for ipnetstr in _CLIENT_IP_FILTER:
        if ipaddr.IPv4Address(src_addr) in ipaddr.IPv4Network(ipnetstr):
            return _PACKET_DIRECTION_CLIENT
        if ipaddr.IPv4Address(dst_addr) in ipaddr.IPv4Network(ipnetstr):
            return _PACKET_DIRECTION_SERVER
    for ipnetstr in _SERVER_IP_FILTER:
        if ipaddr.IPv4Address(src_addr) in ipaddr.IPv4Network(ipnetstr):
            return _PACKET_DIRECTION_SERVER
        if ipaddr.IPv4Address(dst_addr) in ipaddr.IPv4Network(ipnetstr):
            return _PACKET_DIRECTION_CLIENT
    return
    
def process_packet(pkthdr, data):
    if data[12:14]=='\x08\x00':
        ip_d = decode_ip_packet(data[14:])
        print "%s > %s" % (ip_d['source_address'], ip_d['destination_address'])
        pkt_dir = packet_direction(ip_d)
        if pkt_dir == _PACKET_DIRECTION_CLIENT:
            _DUMPER_CLIENT.dump(pkthdr, data)
        elif pkt_dir == _PACKET_DIRECTION_SERVER:
            _DUMPER_SERVER.dump(pkthdr, data)
        else:
            return
        
if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Program to split pcap traces into client and\
server sides in order to be used by TCPREPLY.")
    #parser.add_argument('-r', dest='ifregex', type=boolean, default=False, help="")
    parser.add_argument('--client', type=str, default=None, help="Client network masks (seperated by ',').\
E.g., --client 10.0.0.0/8,20.0.0.0/8")
    parser.add_argument('--server', type=str, default=None, help="Server network masks (seperated by ',').\
E.g., --client 10.0.0.0/8,20.0.0.0/8")
    parser.add_argument('--pcapfile', type=str, default=None, help="Input pcap file")
    args = parser.parse_args()
    #_USE_REGEX = args.ifregex
    clientip = args.client
    serverip = args.server
    pcapfile = args.pcapfile
    # Check the parameters
    if pcapfile == None or (clientip, serverip) == (None, None):
        parser.print_help()
        exit(-1)
    else:
        if not os.path.exists(pcapfile):
            print "pcap file doesn't exist"
            exit(-1)
        if clientip != None:
            _CLIENT_IP_FILTER = clientip.split(',')
        if serverip != None:
            _SERVER_IP_FILTER = serverip.split(',')
        for ipmask in _CLIENT_IP_FILTER+_SERVER_IP_FILTER:
            ip_regex = re.compile(r'^((?:\d{1,3}\.){3}\d{1,3})\/(\d{1,2})')
            ip_res = ip_regex.search(ipmask)
            if  ip_res == None:
                print "Invalid client/server IP format"
                exit(-1)
            else:
                ip = ip_res.group(1)
                mask = ip_res.group(2)
                if not (1<=int(mask)<=32):
                   print "Invalid netmask which would be 1<=mask<=32"
                   exit(-1) 
    # Process the pcap file
    _PCAP_READER = pcapy.open_offline(pcapfile)
    _DUMPER_CLIENT = _PCAP_READER.dump_open(_OUT_CLIENT_FILE)
    _DUMPER_SERVER = _PCAP_READER.dump_open(_OUT_SERVER_FILE)
    try:
        _PCAP_READER.loop(-1, process_packet)
    except KeyboardInterrupt:
      print '%s' % sys.exc_type
      print 'shutting down'
    
