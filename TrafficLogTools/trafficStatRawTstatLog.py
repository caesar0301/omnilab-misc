#!/usr/bin/env python
# Script to have a breakdown of TSTAT log output.
# The output data can be used by R to plot.
#
# This script obtains the statistics about TCP and UDP traffic from Tstat output.
# The TCP statistics contains both complete and incomplete flows, which is stored in
# "log_tcp_complete" and "log_tcp_nocomplete" respectively.
# Each line in the output gives the traffic breakdown during a hour;
# from the second ahead, the first five values give FLOW COUNT, UL PACKETS, DL PACKETS,
# UL BYTES and DL BYTES about TCP, and the left gives those about UDP.

# NOTE:The BYTES values present only the payload volume without header consumpution 
# carried by TCP and UDP. 
# And the directions of upload and download are determined by the "IP_REGEX" parameter
# that gives the source IP pattern in the script.
#
__author__ =  'chenxm'
__email__ = 'chenxm35@gmail.com'


## We modify the gzip only to disable CRC check
import os
import sys
import re
from glob import glob
from datetime import datetime

import pytz
from cStringIO import StringIO
import PyOmniMisc.utils.gzip_mod as gzip_mo


IP_REGEX = '^111\.186.*'


if len(sys.argv) != 2:
	print("Usage: program <tstat_out_folder>")
	exit(-1)
else:
	TSTAT_FOLDER = sys.argv[1]


class Statistics(object):
	def __init__(self):
		self.tcp_packets_up = 0
		self.tcp_packets_down = 0
		self.tcp_flows = 0
		self.tcp_data_bytes_up = 0
		self.tcp_data_bytes_down = 0
		self.udp_packets_up = 0
		self.udp_packets_down = 0
		self.udp_flows = 0
		self.udp_data_bytes_up = 0
		self.udp_data_bytes_down = 0

	def __str__(self):
		s =  "type  %15s  %15s  %15s  %15s  %15s\n" % ('flows', 'packets_up', 'packets_down', 'dbytes_up', 'dbytes_down')
		s += "----  %15s  %15s  %15s  %15s  %15s\n" % tuple(['-'*15] * 5)
		s += " tcp  %15d  %15d  %15d  %15d  %15d\n" % (self.tcp_flows, self.tcp_packets_up, 
		self.tcp_packets_down, self.tcp_data_bytes_up, self.tcp_data_bytes_down)
		s += " udp  %15d  %15d  %15d  %15d  %15d\n" % (self.udp_flows, self.udp_packets_up,
		self.udp_packets_down, self.udp_data_bytes_up, self.udp_data_bytes_down)
		return s

	def asline(self):
		s = "%d\t%d\t%d\t%d\t%d\t" % (self.tcp_flows, self.tcp_packets_up, 
                self.tcp_packets_down, self.tcp_data_bytes_up, self.tcp_data_bytes_down)
		s += "%d\t%d\t%d\t%d\t%d" % (self.udp_flows, self.udp_packets_up,
                self.udp_packets_down, self.udp_data_bytes_up, self.udp_data_bytes_down)
		return s


def extract_datetime(auto_folder="20_00_10_May_2013.out"):
	"""
	To extract datetime from subfolder name created by tstat automatically.
	E.g., '20_00_10_May_2013.out'
	"""
	datestr = auto_folder.rsplit('.')[0]
	dateobj = datetime.strptime(datestr, "%H_%M_%d_%b_%Y")
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
	fos = open('tcp_stat.txt', 'ab')
	fos.write("{0:%Y}-{0:%m}-{0:%d}-{0:%H}\t{1}\n".format(collection_item[0], 
	collection_item[2].asline()))
	fos.close()


# MAIN
collections = []	# [(datetime, pathname, statistics)]

for each_hour in glob(os.path.join(TSTAT_FOLDER, "*.out")):
	period = extract_datetime(os.path.basename(each_hour))
	period = period.replace(minute = 0, second = 0)
	collections.append((period, each_hour, Statistics()))
collections.sort(None, key=lambda x: x[0])

print("Find %d subfolders..." % len(collections))

i = 0
for item in collections:
	period = item[0]
	filepath = item[1]
	statistics = item[2]

	print "Processing %s" % str(period)
	log_tcp_complete = glob(os.path.join(filepath, 'log_tcp_complete*'))[0]
	print log_tcp_complete
	fh = open_file(log_tcp_complete)
	for line in fh:
		line = line.strip('\r \n')
		if len(line) == 0:
			continue
		statistics.tcp_flows += 1
		
		params = line.split(' ')
		if len(params) < 53:
			continue
		try:
			addr_client = params[0]
			addr_server = params[44]
			packets_client = int(params[2])
			dbytes_client = int(params[8])
			packets_server = int(params[46])
			dbytes_server = int(params[52])
		except:
			continue
		
		inCampus = (re.match(IP_REGEX, addr_client) != None) and True or False
		
		if (inCampus):
			statistics.tcp_packets_up += packets_client
			statistics.tcp_data_bytes_up += dbytes_client
			statistics.tcp_packets_down += packets_server
			statistics.tcp_data_bytes_down += dbytes_server
		else:
			statistics.tcp_packets_up += packets_server
                        statistics.tcp_data_bytes_up += dbytes_server
                        statistics.tcp_packets_down += packets_client
                        statistics.tcp_data_bytes_down += dbytes_client
	fh.close()

	log_tcp_noncomplete = glob(os.path.join(filepath, 'log_tcp_nocomplete*'))[0]		
	print log_tcp_noncomplete
	fh = open_file(log_tcp_noncomplete)
	for line in fh:
            	line = line.strip('\r \n')
		if len(line) == 0:
			continue
		statistics.tcp_flows += 1
		params = line.split(' ')
		if len(params) < 53:
			continue

		try:
                        addr_client = params[0]
                        addr_server = params[44]
                        packets_client = int(params[2])
                        dbytes_client = int(params[8])
                        packets_server = int(params[46])
                        dbytes_server = int(params[52])
                except:
                        continue

                flag = re.match(IP_REGEX, addr_client) != None and True or False

                if (flag):
                        statistics.tcp_packets_up += packets_client
                        statistics.tcp_data_bytes_up += dbytes_client
                        statistics.tcp_packets_down += packets_server
                        statistics.tcp_data_bytes_down += dbytes_server
                else:
                        statistics.tcp_packets_up += packets_server
                        statistics.tcp_data_bytes_up += dbytes_server
                        statistics.tcp_packets_down += packets_client
                        statistics.tcp_data_bytes_down += dbytes_client
	fh.close()
	
	log_udp_complete = glob(os.path.join(filepath, 'log_udp_complete*'))[0]
	print log_udp_complete
	fh = open_file(log_udp_complete)
	for line in fh:
		line = line.strip('\r \n')
		if len(line) == 0:
			continue
		statistics.udp_flows += 1
		params = line.split(' ')
		if len(params) < 14:
			continue

		try:
                        addr_client = params[0]
                        addr_server = params[8]
                        packets_client = int(params[5])
                        dbytes_client = int(params[4])
                        packets_server = int(params[13])
                        dbytes_server = int(params[12])
                except:
                        continue

                flag = re.match(IP_REGEX, addr_client) != None and True or False

                if (flag):
                        statistics.udp_packets_up += packets_client
                        statistics.udp_data_bytes_up += dbytes_client
                        statistics.udp_packets_down += packets_server
                        statistics.udp_data_bytes_down += dbytes_server
                else:
                        statistics.udp_packets_up += packets_server
                        statistics.udp_data_bytes_up += dbytes_server
                        statistics.udp_packets_down += packets_client
                        statistics.udp_data_bytes_down += dbytes_client
	fh.close()

	print item[2]
	write_statistics(item)
