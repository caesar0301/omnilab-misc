#!/usr/bin/env python
# Extract web trees in omniperf traces.
# Require "http_logs" file to be generated.
#
# By chenxm
#
import os
import sys

from PyOmniMisc.traffic import http

from user import User


def print_usage():
    print("Usage: python exHttp.py <omniperf_trace>")


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
for entry in http.HTTPLogReader(hl):
    if entry is not None:
        etrs.append(entry)
etrs.sort(None, lambda x: x.get('request_timestamp'))

# Create User object and add http entries
user = User(1)
for ee in etrs:
    user.add_entry(ee)

# Dump web trees
of = os.path.join(input_folder, 'webtrees.out')
if os.path.exists(of):
    os.remove(of)
print user.pretty_print(of, False)

print("Done!")