#!/bin/bash
# install.sh </usr/local/bin>

# fail to exit
set -e 
set -o pipefail

echo "Installing ArubaLogUtilities ... "

prefix="/usr/local/bin"
if [ $1 == ""]; then
	echo "Use default installed path '$prefix'"
else
	prefix=$1
fi
mkdir -p "$prefix"

folder=`dirname $0`
javaproj="wifilog-filter"
echo "Building $javaproj ... "
cd $folder/$javaproj && mvn package && cd -

cp $folder/$javaproj/target/wifilogfilter-*.jar $prefix
cp $folder/mark_session_ip.py $prefix
cp $folder/pure_movement.py $prefix
cp $folder/syslog_replayer.py $prefix