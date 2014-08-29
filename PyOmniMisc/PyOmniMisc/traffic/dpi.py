#!/usr/bin/env python
"""
DPI log format:
112.133.214.254 22777 111.186.48.255 24874 1370947679.074807 UDP 37/BitTorrent 1 148
10.255.249.254 0 111.186.55.255 0 1370948062.667608 ICMP 81/ICMP 2 140
"""

__author__ = 'chenxm'

import csv
from _reader import LogEntry, LogReader


_DPI_FIELDS = [
    "source_ip",
    "source_port",
    "dest_ip",
    "dest_port",
    "connection_timestamp",
    "l4_protocol",
    "detected_protocol",
    "packets",
    "bytes"]


class DPILogEntry(LogEntry):
    def __init__(self):
        LogEntry.__init__(self)
        for key in _DPI_FIELDS:
            self[key] = None

    @staticmethod
    def all():
        """ Get all properties of DPI log entry
        """
        return _DPI_FIELDS

    def socket(self):
        """ Get the socket of this entry
        """
        for item in ['source_ip', 'source_port', 'dest_ip', 'dest_port']:
            if self[item] is None:
                assert("Invalid DPI log entry: %s can't be None" % item)
            source = (self['source_ip'], self['source_port'])
        dest = (self['dest_ip'], self['dest_port'])
        return (source, dest)


class DPILogReader(LogReader):
    def __init__(self, dpi_log_name, head = True, quiet = True):
        LogReader.__init__(self, dpi_log_name)
        if ( head ): self.filehandler.readline()
        # consume the first row if head is true
        self._csv_reader = csv.reader(self.filehandler, delimiter = ' ')
        self._quiet = quiet

    def next(self):
        dpi_log_entry = None
        segments = []
        try:
            segments = self._csv_reader.next()
        except StopIteration:
            self.filehandler.close()
            raise StopIteration
        except csv.Error as e:
            if not self._quiet:
                print('WARNNING: file %s, line %d: %s' % \
                    (self.filename, self._csv_reader.line_num, e))
        if len(segments) == len(_DPI_FIELDS):
            dpi_log_entry = DPILogEntry()
            for i in range( 0, len(_DPI_FIELDS) ):
                value = segments[i]
                dpi_log_entry[ _DPI_FIELDS[i] ] = value
            dpi_log_entry['source_port'] = int(dpi_log_entry['source_port'])
            dpi_log_entry['dest_port'] = int(dpi_log_entry['dest_port'])
            dpi_log_entry['connection_timestamp'] = \
                        float(dpi_log_entry['connection_timestamp'])
            dpi_log_entry['packets'] = int(dpi_log_entry['packets'])
            dpi_log_entry['bytes'] = int(dpi_log_entry['bytes'])
        return dpi_log_entry


class _appNote(object):
    ''' class for app
    '''
    def __init__(self, id, sp, cat):
        self.id = id
        self.name = sp
        self.cat = cat


class DPIAppMap(object):
    '''
    Utility to transform between protocol name, ID and categories.
    '''
    def __init__(self):
        i = 0
        self._cat_db = []
        for line in open('ndpi-proto.csv', 'rb'):
            if i != 0:
                line = line.strip('\r\n ')
                if len(line) == 0:
                    continue
                id, sp, cat = line.split('\t')
                self._cat_db.append(_appNote(int(id), sp, cat))
            i += 1

    def protoName(self, id):
        id = int(id)
        for app in self._cat_db:
            if app.id == id:
                return app.name
        return None

    def protoCat(self, id):
        id = int(id)
        for app in self._cat_db:
            if app.id == id:
                return app.cat;
        return None

    def protoIDs(self, cat):
        ids = []
        for app in self._cat_db:
            if app.cat == cat:
                ids.append(app.id)
        return ids

    def protoNames(self, cat):
        ids = self.protoIDs(cat)
        ns = []
        for id in ids:
            ns.append(self.protoName(id))
        return ns


if __name__ == '__main__':
    appcat = DPIAppMap()
    print appcat.protoName(0)
    print appcat.protoCat(0)
    print appcat.protoIDs("IM")
    print appcat.protoNames("IM")
