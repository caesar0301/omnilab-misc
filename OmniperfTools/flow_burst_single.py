#!/usr/bin/env python
# detect flow burst for a single trace file
import os
import sys
import glob
import logging
import stat

import nids
import dpkt # inspect deep packet content


def print_usage():
    print("Usage: python flow_burst_single.py <pcap_file>")

_tcp_pkts = 0
_udp_pkts = 0
_tcp_bag = {} # {addr: [start_ts, end_ts, pkt_cnt, state]}
end_states = (nids.NIDS_CLOSE, nids.NIDS_TIMEOUT, nids.NIDS_RESET)

def handleTcpStream(tcp):
    #print "tcps -", str(tcp.addr), " state:", tcp.nids_state
    global _tcp_pkts
    _tcp_pkts += 1
    if tcp.nids_state == nids.NIDS_JUST_EST:
        ((src, sport), (dst, dport)) = tcp.addr
        if tcp.addr not in _tcp_bag:
            _tcp_bag[tcp.addr] = [None, None, 1, None]
        _tcp_bag[tcp.addr][0] = nids.get_pkt_ts()
        tcp.client.collect = 1  # do not store data
        tcp.server.collect = 1
        tcp.client.collect_urg = 1
        tcp.server.collect_urg = 1
    elif tcp.nids_state == nids.NIDS_DATA:
        if tcp.addr in _tcp_bag:
            _tcp_bag[tcp.addr][2] += 1
    elif tcp.nids_state in end_states:
        if tcp.addr in _tcp_bag:
            _tcp_bag[tcp.addr][1] = nids.get_pkt_ts()
            _tcp_bag[tcp.addr][2] += 1
            _tcp_bag[tcp.addr][3] = tcp.nids_state

          
def handleUdpStream(addrs, payload, pkt):
    global _udp_pkts
    _udp_pkts += 1


if len(sys.argv) < 2:
    print_usage()
    sys.exit(-1)

input_file = sys.argv[1]

nids.param("filename", input_file)
#nids.param("scan_num_hosts", 0)
nids.chksum_ctl([('0.0.0.0/0', False)])

# Loop forever (network device), or until EOF (pcap file)
# Note that an exception in the callback will break the loop!
try:
    nids.init()
    nids.register_tcp(handleTcpStream)
    nids.register_udp(handleUdpStream)
    nids.run()
except nids.error, e:
    print "nids/pcap error:", e
except Exception, e:
    print "misc. exception (runtime error in user callback?):", e

tcps = _tcp_bag.values()
tcps.sort(None, lambda x: x[0], False)
for tcp in tcps:
    if None in tcp:
        continue
    line = '%.3f\t%.3f\t%d\t%d' % (tcp[0], tcp[1]-tcp[0], tcp[2], tcp[3])
    print(line)
