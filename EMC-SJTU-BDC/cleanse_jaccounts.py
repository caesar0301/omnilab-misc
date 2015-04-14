#!/usr/bin/env python
#
# Cleanse JAccount data

ifile = open("jaccount.csv", 'rb')
ofile = open("jaccount2.csv", 'wb')

n = 0
for line in ifile:
	if n == 0: pass

	parts = line.split(',')
	clean = [i.strip('"') for i in parts]

	ofile.write(','.join(clean))

	n += 1