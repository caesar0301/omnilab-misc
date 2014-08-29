#!/bin/bash
# This script is to moving dumped traffic data from local host
# to shared NFS folder which is mounted at /home/nfs/
# This script needs root privelege to run.
#
# See /tmp/dumpwork.log for running log.
#
# Destination folder: /home/nfs/data.sjtu/passive-[year]/SEIEE/[moved_time]
# You'd better rename the folder later in according to the time of starting dumping.
#
# By chenxm

# Global log
LOGFOLDER=/tmp/tcpdump_logs
mkdir -p $LOGFOLDER
LOGGER=$LOGFOLDER/data_move.log

show_help()
{
	echo "Usage: move_data.sh -i INPUT [-o OUTPUT]" && return
}

INPUT=
OUTPUT=output
OPTIND=1
while getopts "h?i:o:" opt; do
	case "$opt" in
		h|\?)
			show_help
			exit 0
			;;
		i) INPUT=$OPTARG
			;;
		o) OUTPUT=$OPTARG
			;;
	esac
done
shift $((OPTIND-1))

if [ -z $INPUT ]; then
	show_help
	exit 0
fi

# MOVE FROM INTPUT TO OUTPUT
if [ ! -e $INPUT/*.pcap ]; then
  echo "No pcap files" | tee -a $LOGGER
else
  echo "`date`: compress data with gzip" | tee -a $LOGGER
  gzip -9 $INPUT/*.pcap && \
  echo "Compress success" >> $LOGGER || \
  echo "Compress failed" >> $LOGGER
fi

DESTFOLDER=$OUTPUT/`date '+%Y%m%d-%H%M%S'`/
mkdir -p $DESTFOLDER
echo "`date`: Move compressed data to: $DESTFOLDER" | tee -a $LOGGER

mv $INPUT/*.gz $DESTFOLDER && \
echo "Movedata success" >> $LOGGER || \
echo "Movedata failed" >> $LOGGER

exit 0
