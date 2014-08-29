#!/usr/bin/env python
import sys

from PyOmniMisc.utils.file import FileReader

def print_usage():
	print "Usage: program tstat_tcp_out"
	
if len(sys.argv) != 2:
	print_usage()
	exit(-1)
	
tstat_tcp_out = sys.argv[1]

sockets = {}

total_lines = 0
incomplete = []
for line in FileReader.open_file(tstat_tcp_out, 'rb'):
	total_lines += 1
	parts = line.split(' ')
	try:
		a_host = parts[0].strip()
		b_host = parts[1].strip()
		a_port = parts[44].strip()
		b_port = parts[45].strip()
	except IndexError:
		incomplete.append(total_lines)
		continue

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
		
print 'Total lines: %d' % total_lines
print 'Incomplete lines: %d' % len(incomplete)
print incomplete
print 'Unique sockets: %d' % total_unique
print 'Double sockets: %d' % total_double
print 'Multiple sockets: %d' % total_multiple