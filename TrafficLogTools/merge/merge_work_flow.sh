#!/bin/bash

if [ $# -lt 4 ]; then
	echo "Usage: work-flow.sh <raw.tcp> <raw.http> <raw.dpi> <movement>"
	exit -1;
fi

rawtcp=$1
rawhttp=$2
rawdpi=$3
movement=$4

mergedhttptcp='./merged-tcp-http-tmp'
mergedtcphttpdpi='./merged-tcp-http-dpi-tmp'

mergeTcpHttpLogs.py $rawtcp $rawhttp
mergeDpi2Tcp.py $rawdpi $mergedhttptcp
mergeMac2Tcp.py $movement $mergedtcphttpdpi
## output to ./merged-traffic-mac-final