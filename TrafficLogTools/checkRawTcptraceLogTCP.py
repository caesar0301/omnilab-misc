#!/usr/bin/env python
import sys

def print_usage():
    print "Usage: program tcptrace_tcp_out"
    
if len(sys.argv) != 2:
    print_usage()
    exit(-1)
    
tcptrace_tcp_out = sys.argv[1]

sockets = {}

total_lines = 0
for line in open(tcptrace_tcp_out, 'rb'):
    total_lines += 1
    parts = line.split(',')
    a_host = parts[1].strip()
    b_host = parts[2].strip()
    a_port = parts[3].strip()
    b_port = parts[4].strip()
    socket = ["%s:%s" % (a_host, a_port), "%s:%s" % (b_host, b_port)]
    socket.sort()
    key = "%s-%s" % (socket[0], socket[1])
    if key not in sockets:
        sockets[key] = 1
    else:
        sockets[key] += 1


total_unique = 0
total_double = 0
total_multiple = 0
for key in sockets.keys():
    if sockets[key] == 1:
        total_unique += 1
    elif sockets[key] == 2:
        total_double += 1
    else:
        total_multiple += 1
        
print 'total tcp records: %d' % total_lines
print 'total unique sockets: %d' % total_unique
print 'total duplicate sockets: %d' % total_double
print 'total multiple sockets: %d' % total_multiple