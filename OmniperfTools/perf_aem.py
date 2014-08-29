#!/usr/bin/env python
# Evaluating Activity-Entity model
#
# By chenxm
#
import os
import sys

import groundtruth
from PyOmniMisc.model.aem import AEM


def print_usage():
    print("Usage: python exHttp.py <omniperf_trace>")

cut_gap = 8 # sec
def modelAEM(etrs):
    print("Modeling AEM ...")
    # Modeling traffic with AEM
    aem  = AEM(etrs, cut_gap)
    withUA = aem.sessionsWithUA()
    withoutUA = aem.sessionsWithoutUA()

    forest = {}
    for ua in withUA:
        ss = withUA[ua]
        for el in ss[1:]:
            trees = aem.model(el)
            if ua not in forest:
                forest[ua] = []
            forest[ua].extend(trees)

    for host in withoutUA:
        nss = withoutUA[host]
        for el in nss[1:]:
            trees = aem.model(el)
            if host not in forest:
                forest[host] = []
            forest[host].extend(trees)
    return forest

# Options
if len(sys.argv) < 2:
    print_usage()
    sys.exit(-1)

# Http log file
input_folder = sys.argv[1]
hl = os.path.join(input_folder, 'http_logs')
if not os.path.exists(hl):
    raise Exception("Sry, I do not find *http_logs*.out in given folder.")
# Read http logs
etrs = groundtruth.readHttpEntries(hl)
if len(etrs) == 0:
    print("No entries")
    sys.exit(-1)

forest = modelAEM(etrs)
forest_gt = groundtruth.modelGT(input_folder)
fms = groundtruth.evaluate(forest, forest_gt)
of = open("perf-aem-c%d.out" % cut_gap, "ab")
for fm in fms:
	if fm != 0:
		of.write("%.3f\n" % fm)