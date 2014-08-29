#!/bin/bash
# install.sh </usr/local/bin>

set -e 
set -o pipefail

echo "Installing 'TrafficRawTools' ... "

prefix="/usr/local/bin"
if [ $1 == ""]; then
	echo "Use default installed path '$prefix'"
else
	prefix=$1
fi
mkdir -p "$prefix"

folder=`dirname $0`
cp $folder/batch-*.sh $prefix
cp $folder/pcap_split_*.py $prefix