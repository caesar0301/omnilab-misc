#!/bin/bash
# 
# Automatic script to capture network traffic with tcpdump tool 
# from nfm suit.
# A sleeping period before the start of work is to avoid conflict 
# with the ending script.
#
# This script need root privilege to run.
#
# See /tmp/dumpwork.log for running log.
#
# by chenxm
LOGFOLDER=/tmp/tcpdump_logs
mkdir -p $LOGFOLDER
LOGGER=$LOGFOLDER/tcpdump_adapter.log

show_help()
{
	echo "Usage: tcpdump_adapter.sh [-h?] -i interface"
	echo "     [-c tcpdump_cmd(tcpdump)] [-o output_folder(tcpdump.out)]"
	echo "     [-n nameflag(/interface/)]"
	return
}

TCPDUMPCMD=tcpdump
NETIF=
OUTPUT=tcpdump.out
TRACENAME=""
OPTIND=1
while getopts "h?c:i:o:n:" opt; do
	case "$opt" in
		h|\?)
			show_help && exit 1
			;;
		c) TCPDUMPCMD=$OPTARG
			;;
		i) NETIF=$OPTARG
			;;
		o) OUTPUT=$OPTARG
			;;
		n) TRACENAME=$OPTARG
			;;
	esac
done
shift $((OPTIND-1))

if [ -z $NETIF ]; then
	show_help && exit 1
fi

if [ -z $TRACENAME ]; then
	TRACENAME=$NETIF
fi

mkdir -p $OUTPUT

FINALCMD="$TCPDUMPCMD -i $NETIF -G 60 -w $OUTPUT/trace_${TRACENAME}_%Y%m%d-%H%M%S.pcap"
echo "running $FINALCMD" && $FINALCMD

if [ $? -ne 0 ]; then
  echo "`date`: Starting tcpdump failed: $FINALCMD" | tee -a $LOGGER
else
  echo "`date`: Starting tcpdump: $FINALCMD" | tee -a $LOGGER
fi

exit 0
