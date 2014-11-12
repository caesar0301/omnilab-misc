#!/usr/bin/env python
#
# Merge individual user's MAC and associated AP into network traffic file.
#
# INPUT:
# the output of wifilog filter.
#
# chenxm35@gmail.com
# 2013-11-20
import sys
import os
import datetime
import logging

import omnipy.utils.gzip_mod as gzip_mod
from omnipy.data.reader import FileReader
from omnipy.data.reader.wifi import ApEntry, LocationDB

# File name patterns
WIFILOG_FN_PATTERN = r'wifilog\d{4}-\d{2}-\d{2}'
WIFILOG_TIME_PATTERN = "%Y-%m-%d"
TRAFFIC_FN_PATTERN = r'\d{8}-\d{4}-tcp-http'
TRAFFIC_TIME_PATTERN = "%Y%m%d-%H%M"
OUT_FOLDER = './merged-traffic-mac-final'
OUT_FILE_SUFFIX = '-traffic-ap.txt'

LOCAL_IP_PREFIX = "111.186"
LOST_REPLACEMENT = "N/A"

def print_usage():
    print "Usage: program <wifilogFolder> <mergedTrafficFolder>"

## Parsing options
if len(sys.argv) == 3:
    wifilog = sys.argv[1]
    trafficlog = sys.argv[2]
else:
    print_usage()
    exit(-1)

#logger
logging.basicConfig(filename=os.path.basename(sys.argv[0]).rsplit('.',1)[0]+'.log',
    level=logging.DEBUG)

try: os.mkdir(OUT_FOLDER)
except: pass

def _traffic_log_prefix(record):
    '''
    Obtain record prefix of {TCP, HTTP}
    '''
    prefix, content = record.split(":", 1)
    return prefix

def _extract_tcp_ip_and_time(tcp_record):
    '''
    Extract ip address and flow start time from TCP record
    Return None if not found
    '''
    prefix, content = tcp_record.split(":", 1)
    try:
        original = content.strip(' \t').split(' ', 1)[1]
    except IndexError:
        return None
    parts = original.split(' ')
    if len(parts) < 100:
        return None
    try:
        src_addr = parts[0]
        dst_addr = parts[44]
        ip_addr = src_addr
        if LOCAL_IP_PREFIX not in src_addr and LOCAL_IP_PREFIX in dst_addr:
            ip_addr = dst_addr
        flow_conn_time = float(parts[97])/1000.0
        return (ip_addr, flow_conn_time)
    except IndexError:
        logging.error('')
        print "ERROR: ", tcp_record
        return None

def _extract_http_ip_and_time(http_record):
    '''
    Extract ip address and flow start time (or http request time) from HTTP record
    return None if not found
    '''
    prefix, original = http_record.split(":", 1)
    parts = original.split(' ', 9)
    if len(parts) < 10:
        return None
    try:
        src_addr = parts[0]
        dst_addr = parts[2]
        ip_addr = src_addr
        if LOCAL_IP_PREFIX not in src_addr and LOCAL_IP_PREFIX in dst_addr:
            ip_addr = dst_addr
        try:
            time = float(parts[5])  # flow start time
        except:
            time = float(parts[9])  # request time instead
        return (ip_addr, time)
    except:
        return None

def _extract_ip_and_time(records):
    '''
    Extract ip address and flow start time (first http request time) from a TCP flow.
    return None if not found
    '''
    for record in records:
        if "TCP" == _traffic_log_prefix(record):
            res = _extract_tcp_ip_and_time(record)
            if res is not None:
                return res
        else:
            res = _extract_http_ip_and_time(record)
            if res is not None:
                return res
    return None

def _extract_time_from_wifilog_filename(fn):
    '''
    Extract timestamp from wifilog file name
    '''
    bname = os.path.basename(fn).split('.',1)[0]
    dt = datetime.datetime.strptime(bname[7:], WIFILOG_TIME_PATTERN)
    dt = dt.replace(hour=0, minute=0, second=0)
    return dt

def _extract_time_from_traffic_filename(fn):
    '''
    Extract timestamp from traffic filename
    '''
    bname = os.path.basename(fn).split('.',1)[0]
    dt = datetime.datetime.strptime(bname[0:13], TRAFFIC_TIME_PATTERN)
    return dt

def _gen_output_file_from_traffic_file(traffic_file_name):
    # write to output file
    traffic_file_time = _extract_time_from_traffic_filename(traffic_file_name)
    out_file_name = traffic_file_time.strftime(TRAFFIC_TIME_PATTERN) + OUT_FILE_SUFFIX
    out_file_path = os.path.join(OUT_FOLDER, out_file_name)
    return out_file_path

def _do_search_db(records, ldb):
    # Extract mac and ap info
    mac_addr = LOST_REPLACEMENT
    ap_name = LOST_REPLACEMENT
    if ldb is not None:
        ip_time = _extract_ip_and_time(records)
        #print ip_time
        if ip_time is not None:
            mac, ap = ldb.getApEntryByIp(ip_time[0], ip_time[1])
            if mac is not None:
                mac_addr = str(mac)
            if ap is not None:
                ap_name = ap.name
    return (mac_addr, ap_name)

def _write2file(records, device_mac, location_ap, ofile_handler):
    '''
    Write processed records to output file
    '''
    for record in records:
        prefix = _traffic_log_prefix(record)
        if prefix == 'TCP':
            parts = record.split(': ', 1)
            new_line = '%s: %s %s %s' % (prefix, device_mac, location_ap, parts[1])
            ofile_handler.write(new_line)
        else:
            ofile_handler.write(record)

def do_merge(wifi_file, traffic_files):
    ldb = None
    if wifi_file and traffic_files:
        ldb = LocationDB(wifi_file)

    for fn in traffic_files:
        print(fn)
        out_file_path = _gen_output_file_from_traffic_file(fn)
        ofile = FileReader.open_file(out_file_path, 'wb')

        ifile = FileReader.open_file(fn)
        one_tcp_flow = []
        for line in ifile:
            # check prefix
            if 'TCP' == _traffic_log_prefix(line):
                if len(one_tcp_flow) == 0:
                    one_tcp_flow.append(line)
                else:
                    mac, ap = _do_search_db(one_tcp_flow, ldb)
                    _write2file(one_tcp_flow, mac, ap, ofile)
                    # reset tcp flow
                    one_tcp_flow = [line]
            else:
                one_tcp_flow.append(line)

        mac, ap = _do_search_db(one_tcp_flow, ldb)
        _write2file(one_tcp_flow, mac, ap, ofile)

        ifile.close()
        ofile.close()

        logging.info('%s completed' % str(fn))

NUM_WORKERS = 1;
def multipleThread(day_files):
    if not isinstance(day_files, dict):
        print("ERROR: the input must be a map.")
        return;

    import Queue
    from threading import Thread

    q = Queue.Queue()
    for item in sorted(day_files.items()):
        q.put(item)

    def worker():
        while True:
            key, value = q.get()
            print(key)
            wifi_file = value[0]
            traffic_files = value[1]
            do_merge(wifi_file, sorted(traffic_files))
            q.task_done()   # tell the queue

    for i in range(NUM_WORKERS):
        t = Thread(target=worker)
        t.daemon = True
        t.start()

    q.join()

def main():
    day_files = {} # {day: [wifilog, [trafficFiles]]}

    # wifilog files
    files = FileReader.list_files(wifilog, WIFILOG_FN_PATTERN)
    for fn in files:
        dt = _extract_time_from_wifilog_filename(fn)
        if dt not in day_files:
            day_files[dt] = [fn, []]    # wifilog without traffic files
        else:
            print("WARNNING: day %s occurs more than once" % str(dt))

    # Traffic files
    files = FileReader.list_files(trafficlog, TRAFFIC_FN_PATTERN)
    for fn in files:
        dt = _extract_time_from_traffic_filename(fn)
        dt = dt.replace(hour=0, minute=0, second=0)
        if dt in day_files:
            day_files[dt][1].append(fn)
        else:
            day_files[dt] = [None, [fn]]
            print("WARNNING: day %s occurs without wifilog found" % str(dt))

    multipleThread(day_files)


if __name__ == "__main__":
    main()
