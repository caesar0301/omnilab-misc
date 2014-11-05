#!/usr/bin/env python
#_*_ encoding: utf-8 _*_
# BDC2014
import sys
import csv
import datetime

import treelib
from numpy import *

__author__ = 'Xiaming Chen'
__email__ = 'chenxm35@gmail.com'


class DataCleanser(object):

    @staticmethod
    def is_country_name(ln):
        if '国' in ln:
            return False
        return True

    @staticmethod
    def clean_city(ln):
        ln = ln.strip('\t ')
        # remove suffix '市'
        ln = ln.decode('utf-8').replace(u'\u5e02', '')
        return ln

def _decay_func(n, lam=0.4):
    return exp(-lam * array(range(1, n+1)))

def _common_names(ns1, ns2):
    common_set = set()
    for n in ns1:
        common = False
        for m in ns2:
            if n in m or m in n:
                common = True
                common_set.add( m if len(m) <= len(n) else n)
                break
        if common:
            break
    return common_set

def _common_index(ns, common_names):
    result = []
    if not ns:
        return result
    for cn in common_names:
        for i in range(0, len(ns)):
            if cn in ns[i]:
                result.append(i)
    return sorted(result)

def name_list_similarity(ns1, ns2):
    r1 = _decay_func(len(ns1), 0.4)
    r2 = _decay_func(len(ns2), 0.4)
    cnames = _common_names(ns1, ns2)
    ind1 = _common_index(ns1, cnames)
    ind2 = _common_index(ns2, cnames)
    return (sum(r1[ind1]) + sum(r2[ind2])) / (sum(r1) + sum(r2))

class EventInfo(treelib.Node):
    def __init__(self):
        treelib.Node.__init__(self)
        self.stime = None
        self.etime = None
        self.lns = []
        self.pns = []
        self.tag = "Event:%s" % self.identifier

    def matches(self, time, lns, pns, sigma=0.2, delta=0.6):
        time = datetime.datetime.strptime(time, "%Y-%m-%d")
        if (time - self.etime).days >= 30:
            return False
        ld = name_list_similarity(self.lns , lns)
        pd = name_list_similarity(self.pns, pns)
        lpd = delta * ld + (1-delta) * pd
        # print lpd
        if lpd >= sigma:
            return True
        return False

    def update(self, time, lns, pns):
        lam = 0.4
        time = datetime.datetime.strptime(time, "%Y-%m-%d")
        assert isinstance(lns, list)
        assert isinstance(pns, list)
        if self.stime is None:
            self.stime = time
            self.etime = time
            self.lns += lns
            self.pns += pns
        else:
            if time > self.etime:
                self.etime = time
            contribution = 0.7
            lns_stat = dict(zip(self.lns, _decay_func(len(self.lns), lam)))
            pns_stat = dict(zip(self.pns, _decay_func(len(self.pns), lam)))
            lns_stat_new = _decay_func(len(lns), lam)
            pns_stat_new = _decay_func(len(pns), lam)
            for i in range(0, len(lns)):
                if lns[i] not in lns_stat:
                    lns_stat[lns[i]] = 0
                lns_stat[lns[i]] += lns_stat_new[i] * contribution
            for i in range(0, len(pns)):
                if pns[i] not in pns_stat:
                    pns_stat[pns[i]] = 0
                pns_stat[pns[i]] += pns_stat_new[i] * contribution
            lns_new = sorted(lns_stat.items(), key=lambda x: x[1], reverse=True)
            pns_new = sorted(pns_stat.items(), key=lambda x: x[1], reverse=True)
            self.lns = [i[0] for i in lns_new if i[1] > 0.001]
            self.pns = [i[0] for i in pns_new if i[1] > 0.001]
        return

def select_news_fields(n):
    ''' Select several useful fields from an entire news:
    ids, time, location, people and organization names.
    '''
    lns = {} # Location names
    pns = {} # People names

    def update_counter(ns, d):
        if ns not in d:
            d[ns] = 0
        d[ns] += 1

    # Select favorite fields from segresult
    for item in n[16].split(' '):
        item = item.strip(' ')
        if item == '':
            continue
        parts = item.rsplit('/', 1)
        if len(parts) != 2:
            continue
        content, flag = parts
        content = content.strip(' ')
        if content == '':
            continue
        if flag == 'nr':
            update_counter(content, pns)
        elif flag == 'ns' and DataCleanser.is_country_name(content):
            update_counter(content, lns)
        else:
            pass
    # Sort names by frequency
    return [n[1], # ID
        n[8],   # siteurl
        n[5],   # time
        n[3],   # type
        n[6],   # title
        n[9],   # tag
        ';'.join([e[0] for e in sorted(lns.items(), key=lambda x: x[1], reverse=True)]), # Locations
        ';'.join([e[0] for e in sorted(pns.items(), key=lambda x: x[1], reverse=True)])] # People

def create_event_tree(news):
    bus_event = treelib.Tree()
    bus_event.create_node("BusEvent")
    for nn in news:
        time = nn[2]
        type = nn[3]
        title = nn[4]
        tag = nn[5]
        lns = [DataCleanser.clean_city(i.strip()) for i in nn[6].split(';') if len(i.strip()) > 0]
        pns = [i for i in nn[7].split(';')]
        if '公交' in tag:
            event_info = None
            if len(bus_event.children(bus_event.root)) == 0:
                event_info = EventInfo()
                bus_event.add_node(event_info, parent=bus_event.root)
            else:
                found = False
                for event_info in bus_event.children(bus_event.root):
                    if event_info.matches(time, lns, pns):
                        found = True
                if not found:
                    event_info = EventInfo()
                    bus_event.add_node(event_info, parent=bus_event.root)
            event_info.update(time, lns, pns)
            bus_event.create_node(tag=title, parent=event_info.identifier, data=nn)
    ofile = open('event_tree.txt', 'wb')
    ofile.write("Total: %d\n" % len(bus_event.children(bus_event.root)))
    bus_event.save2file('event_tree.txt')

def main():
    if len(sys.argv) < 3:
        print("Usage: detect_event <input> <output>")
        exit(-1)

    input = sys.argv[1]
    output = sys.argv[2]

    csv.field_size_limit(sys.maxsize/2)
    csv.register_dialect('mycsv', delimiter=',', escapechar='\\',
        quotechar='"', lineterminator='\r\n')

    # Read logs and select interested columns
    print("Reading news from file ...")
    news = []
    with open(input, 'rb') as f:
        for line in csv.reader(f, 'mycsv'):
            columns = select_news_fields(line)
            news.append(columns)
    news = sorted(news, key=lambda x: x[2])

    print("Detecting events from news ...")
    create_event_tree(news)

    ofile = open(output, 'wb')
    for nn in news:
        ofile.write(','.join([str(i) for i in nn]))
        ofile.write('\n')
    ofile.close()


if __name__ == "__main__":
    main()
