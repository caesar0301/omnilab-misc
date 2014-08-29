#!/usr/bin/env python
# Evaluating the type model of Choi etc.
#
# By chenxm
#
import os
import sys

from PyOmniMisc.traffic.http import HTTPLogEntry
from PyOmniMisc.model.webtree import WebTree
import groundtruth


def print_usage():
    print("Usage: python exHttp.py <omniperf_trace>")


def is_pred_entity(E): # improve the quality
    if 'text' in str(E.type()):
        return True
    return False


def modelStreamStructure(http_entries):
    # Modeling traffic with StreamStructure
    assert isinstance(http_entries[0], HTTPLogEntry)
    http_entries.sort(key=lambda x:x.rqtstart())
    entities = {}
    for e in http_entries:
        ua = e.ua()
        if ua not in entities:
            entities[ua] = []
        entities[ua].append(e)
    # temporal results
    forest_tmp = {}
    for ua in entities:
        if ua not in forest_tmp:
            forest_tmp[ua] = []
        forest_tmp[ua].extend(WebTree.plant(entities[ua]))
    # finalize the forest with cutting suggested by StreamStructure
    forest = {}
    for ua in forest_tmp:
        wts = forest_tmp[ua]
        for wt in wts[::-1]:
            rn = []
            reverse_nodes = []
            for node in wt.expand_tree(mode=WebTree.WIDTH):
                reverse_nodes.append(node)
            for node in reverse_nodes[::-1]: # Reversed width-first search
                if is_pred_entity(wt[node].pl) and len(wt.is_branch(node)) > 3 and node != wt.root:
                    rn.append(node)
            for n in rn:
                st = WebTree(tree=wt.remove_subtree(n))
                wts.append(st)
        forest[ua] = wts

    for ua in forest:
    	for tree in forest[ua]:
    		tree.show()

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

forest = modelStreamStructure(etrs)
forest_gt = groundtruth.modelGT(input_folder)
fms = groundtruth.evaluate(forest, forest_gt)
of = open("perf_streamstructure.out", "ab")
for fm in fms:
    if fm != 0:
        of.write("%.3f\n" % fm)