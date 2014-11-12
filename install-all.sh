#!/bin/bash
# install.sh </usr/local/bin>

set -e 
set -o pipefail

echo "Installing omnilab-misc tools ... "

easy_install -U omnipy

prefix="/usr/local/bin"
if [ $1 == ""]; then
	echo "Use default installed path '$prefix'"
else
	prefix=$1
fi
mkdir -p "$prefix"

folder=`dirname $0`
cd $folder
install="./ArubaLogUtilities/install.sh"
chmod +x $install && sudo $install
install="./TrafficLogTools/install.sh"
chmod +x $install && sudo $install
install="./TrafficRawTools/install.sh"
chmod +x $install && sudo $install
cd -

chmod -R +x $prefix/*
