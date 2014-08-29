#!/bin/bash

if [ $# -ne 1 ]; then
        echo "Usage: $0 <outputfolder>" && exit 1;
else
        outfolder=$1
fi

LOG_JUST=$outfolder/log_http
LOG_TSTAT=$outfolder/log_tcp
LOG_NDPI=$outfolder/log_dpi

SYSTEM=`uname -s`
if [ $SYSTEM == "Darwin" ]; then
    sec=`date +%s`
    sec=`expr $sec - 86400`
    dateprefix=`date -r $sec +"%Y%m%d"`
    dateyear=`date -r $sec +"%Y"`
    dateday=`date -r $sec +"%d"`
else
    # for linux
    dateprefix=`date -d yesterday +"%Y%m%d"`
    dateyear=`date -d yesterday +"%Y"`
    dateday=`date -d yesterday +"%d"`
fi

#find $LOG_JUST/$dateprefix*.jn.out
gzip -9 $LOG_JUST/$dateprefix*
gzip -9  $LOG_NDPI/$dateprefix*
gzip -9  $LOG_TSTAT/*$dateday*$dateyear.out/*

exit 1;
