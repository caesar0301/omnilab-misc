#!/usr/bin/env python
# Ground truth for evaluating Activity-Entity model
#
# By chenxm
#
import os
import sys
import numpy
from PyOmniMisc.traffic.http import HTTPLogReader
from PyOmniMisc.utils import stat
from PyOmniMisc.model.webtree import WebTree


def readUserClickTS(fn):
    # read user click time series
    ucts = []
    i = 0
    for line in open(fn, 'rb'):
        if i != 0:
            line = line.strip('\r\n ')
            if len(line) == 0: continue
            ucts.append(float(line.split('\t')[0]))
        i+=1
    return ucts


def readHttpEntries(fn):
    # read http logs
    etrs = []
    for entry in HTTPLogReader(fn):
        if entry is not None:
            etrs.append(entry)
    etrs = [e for e in etrs if e.rqtstart() != None] # remove entity without request times
    etrs.sort(key=lambda x: x.rqtstart()) # sort entities by request times
    return etrs


def modelGT(trace_folder):
	print("Modeling groudtruth..")
	# User click files
	uc = os.path.join(trace_folder, 'userclicks2.out')
	if not os.path.exists(uc):
	    uc = os.path.join(trace_folder, 'userclicks.out')
	    if not os.path.exists(uc):
	        raise Exception("Sry, I do not find userclicks*.out in given folder.")
	# Read user clicks
	ucts = readUserClickTS(uc)
	if len(ucts) == 0:
	    print("No click times")
	    sys.exit(-1)
	print len(ucts)

	# Http log file
	hl = os.path.join(trace_folder, 'http_logs')
	if not os.path.exists(hl):
	    raise Exception("Sry, I do not find *http_logs*.out in given folder.")
	# Read http logs
	etrs = readHttpEntries(hl)
	if len(etrs) == 0:
	    print("No entries")
	    sys.exit(-1)

	# prepare data...
	ua_ets = {}
	for e in etrs:
		ua =  e.ua()
		if ua not in ua_ets:
			ua_ets[ua] = []
		ua_ets[ua].append(e)
	# time model
	forest = {}
	for ua in ua_ets:
		if ua not in forest:
			forest[ua] = []
		last = None
		tree = []
		for e in ua_ets[ua]:
			if last is None:
				tree.append(e)
			else:
				if e.rqtstart() - last.rqtstart() <= 3: # sec, request gap
					tree.append(e)
				elif len(tree) != 0:
					forest[ua].append(tree)
					tree = []
			last = e
	# click times
	for ua in forest:
		removed = []
		for tree in forest[ua]:
			found = False
			for node in tree:
				for ts in ucts:
					if node.rqtstart() - ts < 2:
						found = True
						break
				if found: break
			if not found:
				removed.append(tree)
		for r in removed:
			forest[ua].remove(r)
	return forest

def overlap_portion(t1, t2): #  t1 covers t2
	""" We user FMeasure to measure the distance between two tree
	As for t1 covering t2, t2 is treated as the true value, and
	t1 is the predicted value.
	"""
	dup = overlap_cnt(t1, t2)
	recall = dup/len(t2)
	precision = dup/len(t1)
	if recall == 0 and precision == 0:
		return None
	return stat.FMeasure(precision, recall)


def overlap_cnt(t1, t2):#  t1 covers t2
	if not isinstance(t1, list) or not isinstance(t2, list) or \
		len(t1) == 0 or len(t2) == 0:
		raise ValueError("Invalid parameters: list required")
	dup = 0.0
	for e1 in t1:
		for e2 in t2:
			if e1 == e2:
				dup +=1
				break
	return dup


def evaluate(forest, forest_gt):
	print "Evaluation result:"
	uas_target = set(forest.keys())
	uas_gt = set(forest_gt.keys())
	uas = uas_target & uas_gt

	res = []
	for ua in uas:
		print ua
		trees_gt = forest_gt[ua]
		trees_target = []
		for o in forest[ua]:
			# convert format
			if isinstance(o, WebTree):
				tree = o.fruits()
				trees_target.append(tree)
			elif isinstance(o, list):
				trees_target.append(o)
		# evaluate
		print "Target: %d, GT: %d" % (len(trees_target),len(trees_gt))
		# Entity classified accuracies (in two modes):

		# Trace level accuracy--------------------------
		fms = []
		for t1 in trees_gt:
			mx = 0 # match percentage
			for t2 in trees_target:
				p = overlap_portion(t2, t1)
				if p is not None and p > mx:
					mx = p
			fms.append(mx)
		if len(fms) > 0:
			m = numpy.mean(fms)
			print m
			res.append(m)
		#-----------------------------------------------

		# Activity level accuracy-----------------------
		# fms = []
		# for t1 in trees_gt:
		# 	mx = 0
		# 	for t2 in trees_target:
		# 		p = overlap_portion(t2, t1)
		# 		if p is not None and p > mx:
		# 			mx = p
		# 	fms.append(mx)
		# print fms
		# res.extend(fms)
		#-----------------------------------------------

	return res