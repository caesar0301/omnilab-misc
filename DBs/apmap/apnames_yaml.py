#!/usr/bin/env python
# encoding: utf-8
import sys

__version__ = "0.3.5"

def main():
    inputfile = 'apnames-utf8.csv'
    ofile = open('apnames-utf8-%s.yaml' % __version__,'wb')

    ofile.write("%%APNAMES %s # Copyright OMNILab\n" % __version__)
    ofile.write("---\n")
    ofile.write("apprefix_sjtu:\n")
    for line in open(inputfile, 'rb'):
        line = line.strip('\r\n ')
        if len(line) == 0:
            continue

        parts = line.split(',')
        bldname, blddsp, bldrole, bldschool = parts[0:4]
        if 'null' in [bldname, blddsp]:
            continue
        print blddsp

        lon, lat = parts[4:6]

        # dump data to yaml file
        ofile.write("  %s:\n" % bldname)
        ofile.write("    name: '%s'\n" % blddsp)
        ofile.write("    type: '%s'\n" % bldrole)
        ofile.write("    user: '%s'\n" % bldschool)
        ofile.write("    lat: '%s'\n" % lat)
        ofile.write("    lon: '%s'\n" % lon)
    ofile.write("...")
    ofile.close()

if __name__ == '__main__':
	main()
