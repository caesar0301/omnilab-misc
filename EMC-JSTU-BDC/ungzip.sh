#!/bin/bash
# Simply read and write gziped files on HDFS.

if [ $# -lt 2 ]; then
	echo "Usage: ungzip.sh <input> <output>"
	exit -1;
fi

PIGCMD=$(which pig)
$PIGCMD -param input=$1 -param output=$2 $(dirname $0)/rw.pig

exit 0;