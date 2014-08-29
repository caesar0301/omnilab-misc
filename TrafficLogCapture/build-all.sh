#!/bin/bash
# Script to setup this project
# Read and run installation manually if it could not run
# on your system.
set -e

## install neccessary packages in ubuntu
apt-get -y install make gcc g++ libpcap-dev libtool libboost-all-dev libboost-dev bison subversion autoconf postfix
# boost > 1.20 required
# centos: yum install boost boost-devel libpcap-devel

## Build path
THISHOME=`pwd $0`
BUILD=$THISHOME/build
INSTALL_BIN=/usr/local/bin
mkdir -p $BUILD

## install libndpi and pcapDPI
cd $BUILD
svn co https://svn.ntop.org/svn/ntop/trunk/nDPI nDPI
cd nDPI && ./configure -with-pic && make && make install
# pcapDPI
cd $BUILD && rm -rf pcapDPI # use newest version
git clone git://github.com/caesar0301/pcapDPI.git pcapDPI
cd pcapDPI
export INCLUDE_PATH=$BUILD/nDPI/src/include
export LIBRARY_PATH=$BUILD/nDPI/src/lib
make && cp ./pcapDPI $INSTALL_BIN

## build justniffer
# For 64bit system build with explicit boost library folder:
# ./configure --with-boost-libdir=/usr/lib64/
cd $BUILD
tar zxf $THISHOME/external/justniffer-0.5.11.tar.gz
cd justniffer-0.5.11
./configure --with-boost-libdir=/usr/lib/x86_64-linux-gnu
make && make install

## build tcptrace
cd $BUILD
tar zxf $THISHOME/external/tcptrace-6.6.7.tar.gz
cd tcptrace-6.6.7 && ./configure && make && cp ./tcptrace $BIN

## build tstat
cd $BUILD
tar zxf $THISHOME/external/tstat-2.3.1.tar.gz
cd tstat-2.3 && ./autogen.sh && ./configure --enable-libtstat
make && make install

## remove temporary files
cd $THISHOME && rm -rf $BUILD

exit 0;
