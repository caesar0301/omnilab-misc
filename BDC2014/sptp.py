#!/usr/bin/env python
#_*_ encoding: utf-8 _*_
# BDC2014
# Spark script to get spatiotemporal info of news
import sys
import csv
from pyspark import SparkContext, StorageLevel
from pyspark.sql import SQLContext, Row

__author__ = 'Xiaming Chen'
__email__ = 'chenxm35@gmail.com'

def split_line(line):
    ''' Split each line of log into parts based on CSV format.
    '''
    line = line.strip('\r\n ')
    csv.register_dialect('mycsv', delimiter=',', escapechar='\\', quotechar='"')
    for l in csv.reader([line.encode('utf-8')], 'mycsv'):
        return l

def select_news_fields(n):
    ''' Select several useful fields from an entire news:
    ids, time, location, people and organization names.
    '''
    lns = set() # Location names
    pns = set() # People names
    ons = set() # Organization names

    for item in n.segresult.split(' '):
        item = item.strip(' ')
        if item == '':
            continue
        content, flag = item.rsplit('/', 1)
        content = content.strip(' ')
        if content == '':
            continue
        if flag == 'nr':
            pns.add(content)
        elif flag == 'ns':
            lns.add(content)
        elif flag == 'nt':
            ons.add(content)
        else:
            pass
    return [n.url_crc, n.siteurl_crc, n.release_day,
            ';'.join(list(lns)),
            ';'.join(list(pns)),
            ';'.join(list(ons))]

def main():
    if len(sys.argv) < 3:
        print("Usage: sptp <input> <output>")
        exit(-1)

    sc = SparkContext(appName="testbdc2014")
    sqlc = SQLContext(sc)

    input = sys.argv[1]
    output = sys.argv[2]

    # Read data and define schema
    data = sc.textFile(input).cache()
    parts = data.map(split_line)
    news = parts.map(lambda p: Row(
        id = p[0],
        url_crc = long(p[1]),
        release_date = p[2],
        source_type = int(p[3]),
        media_name = p[4],
        release_day = p[5],
        title = p[6],
        format_content = p[7],
        siteurl_crc = long(p[8]),
        hit_tag = p[9],
        navigation = p[10],
        abs = p[11],
        content_media_name = p[12],
        words = int(p[13]),
        type = p[14],
        post_source = p[15],
        segresult = p[16]
        ))
    sqlc.inferSchema(news).registerTempTable("news")
    news.map(select_news_fields)\
        .sortBy(lambda x: x[2])\
        .map(lambda x: ','.join([str(i) for i in x]))\
        .saveAsTextFile(output)

if __name__ == "__main__":
    main()
