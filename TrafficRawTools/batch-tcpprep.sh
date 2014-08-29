#!/bin/bash
# README
#
# To preprocess pcap files for tcpreply in a batch mode.
# Files *.pcap under the folder -d will be processed and 
# cache files renamed as *.pcap.cache be generated.
# Working with batch-tcpreply.sh
# 
# by chenxm
# 2012-12

function printinfo(){
	echo "Usage: $0 folder"
	echo "	The folder contains pcap file/s."
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
	for filename in `ls . | grep -e \\\.pcap$`
	do
		echo $filename
		cachename="$filename.cache"
		tcpprep --auto=router --pcap=$filename --cachefile=$cachename
	done
	exit 0;
else
	echo "folder $folder dose not exist"
	printinfo; exit 1;
fi

exit 0;