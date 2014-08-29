#!/bin/bash

DATA=./users

for user in `ls $DATA/`; do
	for trace in `ls $DATA/$user/`; do
		tf=$DATA/$user/$trace
		echo $tf
		./perf_aem.py $tf
		#./perf_streamstructure.py $tf
	done
done