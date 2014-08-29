#!/bin/bash
# install.sh </usr/local/bin>

set -e 
set -o pipefail

echo "Installing 'TrafficLogTools' ... "

prefix="/usr/local/bin"
if [ $1 == ""]; then
	echo "Use default installed path '$prefix'"
else
	prefix=$1
fi
mkdir -p "$prefix"

folder=`dirname $0`
cp $folder/checkRaw*.py $prefix
cp $folder/trafficStatRaw*.py $prefix
cp $folder/merge/merge*.* $prefix