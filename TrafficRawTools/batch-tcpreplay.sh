#!/bin/bash
# README
#
# To replay pcap files with tcpreplay
# All the files under folder will be replayed in a batch mode
# and in a sequence of ordered names.
# Cos' tcpreplay needs to run tcpprep first to generate the *.cache
# file, you shold run batch-tcpreplay.sh for the first step.
#
# by chenxm
# 2012-12

function printinfo(){
	echo "Usage: $0 folder"
	echo "	The folder contains pcap/cache files."
}

if [ $# -lt 1 ]; then
	printinfo && exit 1;
fi

folder=$1
if [ -z $folder ]; then
	echo "folder name can not be empty"
	exit 1;
fi

# Processing file(s)
if [ -d "$folder" ]; then
	cd $folder
	for pcapname in `ls . | grep -e \\\.pcap$ | sort`
	do
		cachename="$pcapname.cache"
		# intf1: server, intf2: client
		tcpreplay --pid --stats=3 --multiplier=1.0 --cachefile=$cachename --intf1=eth1 --intf2=eth2 $pcapname
	done
	exit 0;
else
	echo "folder $folder dose not exist"
	printinfo; exit 1;
fi

exit 0;