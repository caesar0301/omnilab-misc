#!/bin/bash
# This script is to stop the running of tcpdump.
# See /tmp/dumpwork.log for running log.
# This script need root privilege to run.
#
# by chenxm

# Global log
LOGFOLDER=/tmp/tcpdump_logs
mkdir -p $LOGFOLDER
LOGGER=$LOGFOLDER/stop.log

pids=`ps -ef |grep tcpdump|awk '{print $2}'`;
echo "`date`: Stop tcpdump." >> $LOGGER

for pid in $pids
do
  kill -9 "$pid";
  if [ $? -eq 0 ]; then
    echo "$pid: succeeded"
  else
    echo "$pid: failed"
  fi
done

exit 0;