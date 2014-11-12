#!/usr/bin/env python
#
# Add DPI tags to merged TCP and HTTP logs.
#
# ***********
# FUNCTION:
# ***********
# Mark flow protocol signatures identified by nDPI for each TCP flow 
# after the fommer merge operation.
# Flows are matched with socket and timestamp (time drift tolerance).
# The first filed of flow records the layer 7 protocal type if it is
# given by DPI data; otherwise, 'N/A' is recorded to indicate lost DPI data.
#
# **********
# INPUT: 
# **********
# Raw DPI data folder output by PcapEx and the merged HTTP/TCP data
# output by program `mergeTcpHttpLogs.py`.
#
# **********
# OUTPUT:
# **********
# The HTTP/TCP data with DPI flow signature.
# Each file represents for an hour.
#
# **********
# CONTACT:
# **********
# By chenxm
# chenxm35@gmail.com
# Updated: 2013-08-27
#
import os, sys, datetime
import logging

import omnipy.utils.gzip_mod as gzip_mod
from omnipy.data.reader import FileReader

# File name patterns
OUT_FOLDER = './merged-tcp-http-dpi-tmp'
OUT_FILE_SUFFIX = '-tcp-http'
TCP_FN_PATTERN = r'\d{8}-\d{4}-merged.'
TCP_TIME_PATTERN = "%Y%m%d-%H%M"
DPI_FN_PATTERN = r'\d{8}-\d{4}\.dpi.'
DPI_TIME_PATTERN = "%Y%m%d-%H%M"

def print_usage():
    print "Usage: program <raw_dpi_folder> <merged_HTTP_TCP_folder>"

## Parsing options
if len(sys.argv) == 3:
    input_dpi_log = sys.argv[1]
    input_tcp_log = sys.argv[2]
else:
    print_usage()
    exit(-1)

#logger
logging.basicConfig(filename=os.path.basename(sys.argv[0]).rsplit('.',1)[0]+'.log',
    level=logging.DEBUG)

try: os.mkdir(OUT_FOLDER)
except: pass


def ip2int(s):
    "Convert dotted IPv4 address to integer."
    return reduce(lambda a,b: a<<8 | b, map(int, s.split(".")))
 

def int2ip(ip):
    "Convert 32-bit integer to dotted IPv4 address."
    return ".".join(map(lambda n: str(ip>>n & 0xFF), [24,16,8,0]))


def mergeDpi2Tcp(dpi_file, tcp_file, output):
    if not tcp_file:
        return;
    # Load the meta into memory
    print("Loading DPI meta data ...")
    dpi_meta = {} # {socket: [flows]}
    if dpi_file:
        idpi_file = FileReader.open_file(dpi_file, 'rb')
        i = 0
        for line in idpi_file:
            i += 1; line = line.strip("\r \n")
            if i==1 or len(line) == 0: continue
            # Extract DPI meta
            parts = line.split(' ')
            if len(parts) < 7: continue
            try:
                src_addr = ip2int(parts[0]); src_port = int(parts[1])
                dst_addr = ip2int(parts[2]); dst_port = int(parts[3])
                flow_conn_time = float(parts[4])
                l4_proto = parts[5]
                if l4_proto != "TCP": continue
                l7_proto = parts[6]
            except (ValueError, IndexError):
                continue
            # Store in memory
            fkey = sorted([(src_addr, src_port),  (dst_addr, dst_port)])
            fkey = tuple(fkey)
            if fkey not in dpi_meta:
                dpi_meta[fkey] = []
            dpi_meta[fkey].append( (flow_conn_time, l7_proto) )
        idpi_file.close()

    # Mark the TCP files
    print("Adding DPI tag to flows ...")
    ofile = FileReader.open_file(output, 'wb')
    itcp_file = FileReader.open_file(tcp_file, 'rb')
    if len(dpi_meta) > 0:
        for line in itcp_file:
            proto, content = line.split(':', 1)
            content = content.strip(' ')
            if proto == 'TCP':
                parts = content.split(' ')
                if len(parts) < 98:
                    ofile.write("%s\n" % line.strip('\r\n ')); continue
                try:
                    src_addr = ip2int(parts[0])
                    src_port = int(parts[1])
                    dst_addr = ip2int(parts[44])
                    dst_port = int(parts[45])
                    fkey = sorted([(src_addr, src_port),  (dst_addr, dst_port)])
                    fkey = tuple(fkey)
                    try:
                        flow_conn_time = float(parts[97])/1000.0 # in seconds
                    except:
                        print('TCP connection time convertion error: "%s"' % line)
                    p = "N/A"
                    if fkey in dpi_meta:
                        for flow in dpi_meta[fkey]:
                            if abs(flow_conn_time-flow[0]) < 60: # in seconds
                                p = flow[1]; break
                    ofile.write("%s: %s %s\n" % (proto, p, content.strip('\r\n ')))
                except IndexError:
                    ofile.write("%s\n" % line.strip('\r\n '))
            elif proto == 'HTTP':
                # Write directly
                ofile.write("%s\n" % line.strip('\r\n '))
    else:
        # DPI data lost when capturing
        for line in itcp_file:
            proto, content = line.split(':', 1)
            content = content.strip(' ')
            if proto == 'TCP':
                p = "N/A"
                ofile.write("%s: %s %s\n" % (proto, p, content.strip('\r\n ')))
            elif proto == 'HTTP':
                # Write directly
                ofile.write("%s\n" % line.strip('\r\n '))
    itcp_file.close()
    ofile.close()
    logging.info('file %s completed' % tcp_file)


NUM_WORKERS = 1;
def multipleThread(hour_files_map):
    if not isinstance(hour_files_map, dict):
        print("ERROR: the input must be a map.")
        return;

    import Queue
    from threading import Thread

    q = Queue.Queue()
    for item in sorted(hour_files_map.items()):
        q.put(item)

    def worker():
        while True:
            key, value = q.get()
            print("Processing "+str(key)+" ... ")
            ofn = os.path.join(OUT_FOLDER, key.strftime(TCP_TIME_PATTERN)+OUT_FILE_SUFFIX)
            dpi_file = value[0]
            tcp_file = value[1]
            mergeDpi2Tcp(dpi_file, tcp_file, ofn)
            q.task_done()

    for i in range(NUM_WORKERS):
        t = Thread(target=worker)
        t.daemon = True
        t.start()

    q.join()
    

def main():
    # Group raw DPI and TCP files w.r.t. the same hour
    hour_files_map = {} # {hour: [dpi, tcp]}
    files = FileReader.list_files(input_dpi_log, DPI_FN_PATTERN)
    for fn in files:
        bname = os.path.basename(fn)
        dt = datetime.datetime.strptime(bname.split('.',1)[0], DPI_TIME_PATTERN)
        dt = dt.replace(minute=0, second=0)
        if dt not in hour_files_map:
            hour_files_map[dt] = [fn, None]
        else:
            print("WARNNING: Hour %s occurs with more one DPI file found" % str(dt))

    files = FileReader.list_files(input_tcp_log, TCP_FN_PATTERN)
    for fn in files:
        bname = os.path.basename(fn)
        dt = datetime.datetime.strptime(bname.rsplit('-',1)[0], TCP_TIME_PATTERN)
        dt = dt.replace(minute=0, second=0)
        if dt in hour_files_map:
            hour_files_map[dt][1] = fn
        else:
            hour_files_map[dt] = [None, fn]
            print("WARNNING: Hour %s occurs without DPI file found" % str(dt))

    multipleThread(hour_files_map)



if __name__ == '__main__':
    main()
