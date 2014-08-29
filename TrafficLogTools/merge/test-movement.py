#!/usr/bin/env python
import cProfile, pstats
import sys

from PyOmniMisc.wifi.movement import LocationDB

def print_usage():
    print("Usage: python parser.py inputfolder outputfile")
    print("\tThe input is produced by wifilog-filter in java.")

if len(sys.argv) < 3:
    print_usage()
    sys.exit(-1)
else:
    inputfolder = sys.argv[1]
    outputfile = sys.argv[2]

if (not os.path.isdir(inputfolder)):
    print("The input must be a folder.")
    print_usage(); sys.exit(-1)

# Profiling location database initialization
pr = cProfile.Profile()
pr.enable()
ldb = LocationDB(inputfolder)
pr.disable()
ps = pstats.Stats(pr)
#ps.strip_dirs().print_stats()

# serialize database
#ldb.dumpDB(outputfile+".dat")
# load database
#ldb.loadDB(outputfile+".dat")
# dump to file
print("Saving to file: %s" % outputfile)
ldb.save2file(outputfile)