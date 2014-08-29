#!/bin/bash
# Extract http for multiple users of Omniperf.

DATA=/home/chenxm/tera/workspace/Datasets/Omniperf
#DATA=./test

for user in `ls $DATA/`; do
	for trace in `ls $DATA/$user/`; do
		tf=$DATA/$user/$trace
		echo $tf
		./exHttp.py $tf
		./flowBurst.py $tf
		./packetBurst.py $tf
		./userClicks.py $tf
		./exWebTree.py $tf
		./runAEM.py $tf
	done
done