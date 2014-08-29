#!/usr/bin/env python
# Run AEM model on Omniperf traces
#
# Usage:
#     cd OmniperfTools
#     python rumAEM.py trace_folder
#
import os
import sys

from PyOmniMisc.traffic.http import HTTPLogReader
from PyOmniMisc.model.aem import AEM

def print_usage():
    print("Usage: python rumAEM.py <omniperf_trace>")


if len(sys.argv) < 2:
    print_usage()
    sys.exit(-1)

# Check input file : http_logs
input_folder = sys.argv[1]
hl = os.path.join(input_folder, 'http_logs')
if not os.path.exists(hl):
    raise Exception("Sry, I do not find *http_logs*.out in given folder.")

# read http logs
etrs = []
for entry in HTTPLogReader(hl):
    if entry is not None:
        etrs.append(entry)
etrs.sort(key=lambda x: x.rqtstart())
if len(etrs) == 0:
    print("No http logs")
    sys.exit(-1)

aem  = AEM(etrs)
withUA = aem.sessionsWithUA()
withoutUA = aem.sessionsWithoutUA()

# output file
output = os.path.join(input_folder, 'aem.out')
try:
    os.remove(output)
except OSError:
    pass

for ua in withUA:
    ss = withUA[ua]
    open(output, 'ab').write('\n****************** %s\n' % ua)
    for el in ss[1:]:
        trees = aem.model(el)
        for wt in trees:
            #wt.show(key=lambda x: x.pl.rqtstart(), reverse=False)
            #open(output, 'ab').write('\n')
            wt.save2file(output, key=lambda x: x.pl.rqtstart())

for host in withoutUA:
    nss = withoutUA[host]
    open(output, 'ab').write('\n****************** %s\n' % host)
    for el in nss[1:]:
        trees = aem.model(el)
        for wt in trees:
            #wt.show(key=lambda x: x.pl.rqtstart(), reverse=False)
            #open(output, 'ab').write('\n')
            wt.save2file(output, key=lambda x: x.pl.rqtstart())

print("Done!")