#!/usr/bin/env python
#encoding: utf-8
__author__ = 'Jamin X. Chen'
__email__ = 'chen_xm@sjtu.edu.cn'

import sys, os
from omnipy.data.reader import FileReader

def main():
    if len(sys.argv) < 3:
        print("Usage: python pure_movement.py <inputpath> <outputpath>")
        sys.exit(-1)
    inputpath = sys.argv[1]
    outputpath = sys.argv[2]
    try:
    	os.mkdir(outputpath)
    except:
    	print("using an existing folder: %s" % outputpath)

    for filename in FileReader.list_files(inputpath):
        ofilename = os.path.join(outputpath, os.path.basename(filename))
        ofile = FileReader.open_file(ofilename, 'wb')
        total = 0
        valid = 0
        for line in FileReader.open_file(filename):
        	line = line.strip('\r\n ')
        	if len(line)==0: continue
        	total += 1
        	try:
        		mac, stime, etime, dur, ap = line.split('\t')
        	except:
        		continue
        	valid += 1
        	ofile.write("{0}\t{1}\t{2}\t{3}\n".format(mac, stime, etime, ap))
        ofile.close()


if __name__ == '__main__':
    main()