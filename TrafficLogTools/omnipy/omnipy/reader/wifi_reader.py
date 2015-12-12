#coding: utf-8
"""
About this module:
This module aims to parse and store association information extracted
from Aruba Wifi syslog, and provides APIs for external calls.

External program can call to get association information among times,
device MACs, IP addresses, and AP entries.

For details, please refer to README in the root folder.
"""
import os, sys
import re
from time import strptime, mktime, clock

from ._reader import FileReader

__author__ = 'chenxm'
__all__ = ["LocationDB"]


class ApEntry(object):
    """
    Class of AP record entry, containing AP name,
    association start time, and association endtime;
    """
    name_map = {} # save memory
    name_mapr = {}

    def __init__(self, ap_name, start_sec, end_sec):
        if ap_name not in ApEntry.name_map:
            ApEntry.name_map[ap_name] = len(ApEntry.name_map)
        self._id = ApEntry.name_map[ap_name]
        ApEntry.name_mapr[self._id] = ap_name
        self.start = start_sec
        self.end = end_sec

    @property
    def name(self):
        return ApEntry.name_mapr[self._id]


class MacEntry(object):
    """
    Class of IP entry. This class is used by LocationDB.
    """
    def __init__(self):
        # MAC address binded with specific IP
        self.mac = None
        # time when IP was first allocated
        self.atime = None
        # time when IP was recycled
        self.rtime = None
        # flag
        self.is_recycled = False


class LocationDB(object):
    """
    Database of location information extracted from Aruba Wifi syslog.
    """
    def __init__(self, syslog = None, serialized_db = None):
        """
        @param syslog The folder containing filtered wifi syslog files.
        """
        self._ip_mac_db = {} # {IP : [MacEntry]}
        self._mac_ap_db = {} # {MAC: [ApEntry]}
        if serialized_db and os.path.exists(serialized_db):
            self.loadDB(serialized_db)
        elif syslog:
            print("Initializing location database...")
            start = clock()
            self._create_inner_db(syslog)
            print("Initialized in %.3fs" % (clock()-start))


    def _cmp_t(self, sec1, sec2, tolerance = 120):
        t1 = sec2 - tolerance
        t2 = sec2 + tolerance
        if sec1 <= t2 and sec1 >= t1:
            return 0
        elif sec1 > t2:
            return 1
        else:
            return -1

    def getIpMacDatabase(self):
        return self._ip_mac_db


    def getMacApDatabase(self):
        return self._mac_ap_db


    def getMacByIP(self, ip_address, timestamp_sec):
        """
        Get MAC address associated with specific IP at @timestamp_sec.
        This function connect IP traffic with devices.
        @param ip_address The IP address to search
        @param timestamp_sec The unix timestamp in seconds of this IP.
        @return The mac address associated with, or empty list if not found
        """
        macs = []
        if ip_address in self._ip_mac_db:
            for macentry in self._ip_mac_db[ip_address]:
                atime = macentry.atime
                rtime = macentry.rtime
                if self._cmp_t(timestamp_sec, atime) >=0 and self._cmp_t(timestamp_sec, rtime) <=0:
                    #print macentry.mac, timestamp_sec-atime, rtime-atime
                    macs.append(macentry.mac)
        return macs


    def getIpByMac(self, mac_address, timestamp_sec):
        """ Get IP address associated with specific MAC at @timestamp_sec.
        This function connect IP traffic with devices.
        """
        for ip, macs in self._ip_mac_db.items():
            for e in macs:
                if mac_address == e.mac and self._cmp_t(timestamp_sec, e.atime)>=0 and \
                self._cmp_t(timestamp_sec, e.rtime)<=0:
                    return ip
        return None


    def getApEntryByMac(self, mac_address, timestamp_sec):
        """
        Get the AP name associated by specific MAC address at some timestamp
        @param mac_address The MAC address to search
        @param timestamp_sec The unix timestamp in seconds of this MAC.
        @return The AP entry associated, or none if not found
        """
        if mac_address not in self._mac_ap_db:
            return None
        for apentry in self._mac_ap_db[mac_address]:
            if self._cmp_t(timestamp_sec, apentry.start) >= 0 and self._cmp_t(timestamp_sec, apentry.end) <= 0:
                #print apentry.name, timestamp_sec-apentry.start, apentry.end-apentry.start;
                return apentry
        return None


    def getApEntryByIp(self, ip_address, timestamp_sec):
        """
        @param ip_address The IP address to search
        @param timestamp_sec The unix timestamp in seconds of this IP.
        @return The first found of mac address and AP entry tuple, or none if not found
        """
        macs = self.getMacByIP(ip_address, timestamp_sec)
        if len(macs) > 0:
            for mac in macs:
                apent = self.getApEntryByMac(mac, timestamp_sec)
                if apent is not None:
                    return (mac, apent)
            return (mac, None)
        return (None, None)


    def dumpDB(self, filepath):
        """
        Serialize inner database and maintain it in persistent storage.
        It has advantage of that programmers don't need to create the database repeately
        when developing their programs, or to share the database.
        @param filepath The name of file for persistent storage.
        """
        import shelve
        d = shelve.open(filepath)
        d['IpMacDatabase'] = self._ip_mac_db
        d['MacApDatabase'] = self._mac_ap_db
        d.close


    def loadDB(self, filepath):
        """
        Load inner database from persistent storage.
        @param filepath The name of file for persistent storage.
        """
        import shelve
        print("Loading location database...")
        start = clock()
        d = shelve.open(filepath)
        self._ip_mac_db = d['IpMacDatabase']
        self._mac_ap_db = d['MacApDatabase']
        d.close
        print("Loaded in %.3fs" % (clock()-start))


    def save2file(self, filepath):
        """
        Dump the inner database into plain text file.
        This will be useful for debugging purposes.
        """
        ip_mac_ofile = open(filepath+".ip", 'wb')
        mac_ap_ofile = open(filepath+".ap", 'wb')
        for ip in self._ip_mac_db:
            for ipent in self._ip_mac_db[ip]:
                ip_mac_ofile.write("{0}\t{1}\t{2}\t{3}\n".format(ipent.mac, ip, ipent.atime, ipent.rtime))
        ip_mac_ofile.close()
        for mac in self._mac_ap_db:
            for apent in self._mac_ap_db[mac]:
                mac_ap_ofile.write("{0}\t{1}\t{2}\t{3}\n".format(mac, apent.name, apent.start, apent.end))
        mac_ap_ofile.close()


    def _create_inner_db(self, syslog):
        """
        To create a inner database to store the location information.
        """
        if  os.path.isdir(syslog):
            files = FileReader.list_files(syslog, '[0-9a-e]+')    # mac pattern
        elif os.path.isfile(syslog):
            files = [syslog]
        else:
            print("Given path is not a file/folder, exit")
            sys.exit(-1)

        TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        # handle each file
        for file_path in files:
            for line in FileReader.open_file(file_path, 'rb'):
                # remove empty lines
                line = line.strip("\r\n ")
                if len(line) == 0:
                    continue;

                # Extract user mac
                user_mac, left = line.split('\t', 1)
                if re.search(r"ipallocation", left, re.I):
                    # if match IP allocation messages
                    time_str, ip_str = re.split(r"ipallocation", left, 0, re.I)
                    time_str = time_str.strip('\t ')
                    ip_str = ip_str.strip('\t ')
                    if ip_str not in self._ip_mac_db:
                        self._ip_mac_db[ip_str] = []

                    newent = MacEntry()
                    newent.mac = user_mac
                    newent.atime = mktime(strptime(time_str, TIME_FORMAT))
                    newent.rtime = newent.atime

                    added = False
                    for ipent in self._ip_mac_db[ip_str][::-1]: # revsersed order
                        if ipent.mac == newent.mac:
                            if not ipent.is_recycled:
                                # Dup allcation message, update rtime
                                ipent.rtime = newent.atime
                                added = True
                                break
                            elif newent.atime > ipent.rtime:
                                self._ip_mac_db[ip_str].append(newent)
                                added = True
                                break
                    if not added:
                        self._ip_mac_db[ip_str].append(newent)

                    # Sort IP entries by allocation time
                    self._ip_mac_db[ip_str].sort(None, lambda x: x.atime, False)
                elif re.search(r"iprecycle", left, re.I):
                    time_str, ip_str = re.split(r"iprecycle", left, 0, re.I)
                    time_str = time_str.strip('\t ')
                    ip_str = ip_str.strip('\t ')
                    if ip_str not in self._ip_mac_db:
                        # allocation message lost
                        continue
                    ryctime = mktime(strptime(time_str, TIME_FORMAT))
                    for ipent in self._ip_mac_db[ip_str][::-1]: # reversed order
                        if ipent.mac == user_mac:
                            delta = ryctime - ipent.atime
                            if delta <= 24*3600 and delta >= 0:    # sec
                                # make sure it is a valid recycled IP
                                # within 24 hours
                                ipent.rtime = ryctime
                                ipent.is_recycled = True
                                break
                elif re.search("userauth", left, re.I):
                    # do not process up to now.
                    continue
                else:
                    # create a new AP entry from association log
                    start_time_str, end_time_str, duration_str, ap_name = left.split('\t')
                    ap_entry = ApEntry(ap_name,
                        mktime(strptime(start_time_str, TIME_FORMAT)),
                        mktime(strptime(end_time_str, TIME_FORMAT))
                    )
                    if user_mac not in self._mac_ap_db:
                        self._mac_ap_db[user_mac] = []
                    self._mac_ap_db[user_mac].append(ap_entry)