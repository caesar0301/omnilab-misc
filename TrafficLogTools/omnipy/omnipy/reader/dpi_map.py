#!/usr/bin/env python
"""
DPI log format:
112.133.214.254 22777 111.186.48.255 24874 1370947679.074807 UDP 37/BitTorrent 1 148
10.255.249.254 0 111.186.55.255 0 1370948062.667608 ICMP 81/ICMP 2 140
"""
import os

__author__ = 'chenxm'
__all__ = ["DPIMap"]


class _appNote(object):
    ''' class for app
    '''
    def __init__(self, id, sp, cat):
        self.id = id
        self.name = sp
        self.cat = cat


class DPIMap(object):
    '''
    Utility to transform between protocol name, ID and categories.
    '''
    def __init__(self):
        i = 0
        self._cat_db = []
        this_dir, this_file = os.path.split(__file__)
        protofile = os.path.join(this_dir, "..", "..", "ndpi-proto.csv")
        for line in open(protofile, 'rb'):
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