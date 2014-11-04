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

    # Select favorite fields from segresult
    for item in n[16].split(' '):
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
    return [n[1], n[8], n[5],
            ';'.join(list(lns)),
            ';'.join(list(pns)),
            ';'.join(list(ons))]

def main():
    if len(sys.argv) < 3:
        print("Usage: sptp <input> <output>")
        exit(-1)

    sc = SparkContext(appName="testbdc2014")

    input = sys.argv[1]
    output = sys.argv[2]

    # Read data
	# 'id': str,
	# 'url_crc': long,
	# 'release_date': str,
	# 'source_type': str,
	# 'media_name': int,
	# 'release_day': str,
	# 'title': str,
	# 'format_content': str,
	# 'siteurl_crc': long,
	# 'hit_tag': str,
	# 'navigation': str,
	# 'abs': str,
	# 'content_media_name': str,
	# 'words': int,
	# 'type': str,
	# 'post_source': str,
	# 'segresult': str
    news = sc.textFile(input).map(split_line)
    news.map(select_news_fields)\
        .sortBy(lambda x: x[2])\
        .map(lambda x: ','.join([str(i) for i in x]))\
        .saveAsTextFile(output)

if __name__ == "__main__":
    main()
