#!/bin/bash

if [ $# -lt 2 ]; then
	echo "Usage: run_cleanse_http_logs.sh <input> <output>"
	exit -1;
fi

# remove running logs
rm -rf pig_*.log

PIGCMD=$(which pig)
OUTPUT=$2-$(date +"%Y%M%d%H%M%S")
echo "Output to $OUTPUT"

$PIGCMD -param input=$1 -param output=$OUTPUT $(dirname $0)/cleanse_http_logs.pig

exit 0;