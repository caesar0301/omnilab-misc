#!/bin/bash
# Automatic script to run traffic logger utilities.
# By chenxm
# chenxm35@gmail.com

THISHOME=$(dirname $0)

## Print usage information
printUsage(){
    echo "Usage: $0 [[-i inf/pcap] [-o output] start]|stop|status";
}

## Find utilities from system binary folder
findUtility(){
    local util=$1
    for BINPATH in /bin /usr/bin /usr/local/bin
    do
        util=`find $BINPATH -type f -name $1`
        if [ $util ]; then
            break
        fi
    done
    if [ -z $util ]; then
        echo "Cannot find utility '$1' from system path. Quit."
        exit -1
    else
        echo "$util"
        return 1
    fi
}

## Check the existence of utilities
## Quit script if they are not found
checkUtils(){
    findUtility tstat
    findUtility justniffer
    findUtility pcapDPI
}

## Start command
start(){
    # Installed binary utilities.
    CMD_TSTAT=$(findUtility tstat)
    CMD_JUSTNIFFER=$(findUtility justniffer)
    CMD_PCAPDPI=$(findUtility pcapDPI)

    # Network interface to sniff.
    INTERFACE=$netinf
    OUTPERMONTH=$outfolder/`date +%Y%m`
    mkdir -p $OUTPERMONTH

    # Create each folder with the name taged by datetime
    # e.g., 20130101-0100*
    datetime=`date '+%Y%m%d-%H%M'`

    # Output log folder names
    TSTAT_LOG="tcp"
    JUSTNIFFER_LOG="http"
    PCAPDPI_LOG="dpi"

    # Run tstat utility
    # Network configuration denotes source and destination network IP addresses.
    # All output logs are compressed by gzip.
    mkdir -p $OUTPERMONTH/$TSTAT_LOG
    TSTAT_NET_CONF=$THISHOME/../conf/tstat-net.conf
    $CMD_TSTAT -Z -l -i $INTERFACE -N $TSTAT_NET_CONF -s $OUTPERMONTH/$TSTAT_LOG  &

    # Run justniffer utility
    # We have a predefined configuration files about HTTP message fields.
    # The suffix "light" means we only capture neccessary fields as we need.
    # All output logs are compressed by gzip.
    JUSTNIFFER_CONF=$THISHOME/../conf/justniffer-light.conf
    mkdir -p $OUTPERMONTH/$JUSTNIFFER_LOG
    $CMD_JUSTNIFFER -i $INTERFACE -F -c $JUSTNIFFER_CONF > $OUTPERMONTH/$JUSTNIFFER_LOG/$datetime.jn.out  &

    # Run pcapDPI utility.
    # The output is dump at the tail of each hour.
    mkdir -p $OUTPERMONTH/$PCAPDPI_LOG
    $CMD_PCAPDPI -i $INTERFACE -w $OUTPERMONTH/$PCAPDPI_LOG/$datetime.dpi.out  &

    wait
}

## Stop utilities
stop(){
    PID=$(cat "/tmp/traffic-logger.pid")
    echo "Stopping traffic logger PID=$PID..."
    ## Kill process tree
    if [ -n $PID ]; then
        CPIDS=`pgrep -P $PID`
        echo "Children PIDs: $CPIDS"
        if [ -n "$CPIDS" ]; then
            kill -2 $CPIDS;
            echo "Sleeping 60 seconds to dump live data..."
            sleep 2 && kill -9 $CPIDS
        fi
    fi
    ## Make sure all processes are terminated
    echo "Make sure all subprocesses are cleared..."
    kill -9 `ps -aux |grep justniffer | awk '{print $2}'`
    kill -9 `ps -aux |grep tstat | awk '{print $2}'`
    kill -9 `ps -aux |grep pcapDPI | awk '{print $2}'`
    echo "Stopped!"
}

## Report running status
status(){
    PID=$(cat "/tmp/traffic-logger.pid")
    if [ -n "$PID" ]; then
        CPIDS=$(pgrep -P $PID)
        if [ -n "$CPIDS" ]; then
            echo "Traffic logger is running: PID=$PID";
            return 1;
        fi
    fi
    echo "No traffic logger is running."
}


## Parse options
if [ $# -lt 1 ]; then
    printUsage && exit 1;
fi
scmd=`echo "${@: -1}"`
if [ "$scmd" = "start" ]; then
    while getopts i:o:h opt;
    do
        case "$opt" in
            h) printUsage && exit 1;;
            i) netinf="$OPTARG";;
            o) outfolder="$OPTARG";;
            ?) printUsage && exit 1;;
        esac
    done
    if [ -z $netinf ] || [ -z $outfolder ]; then
        echo "ERROR: absent packet source or output folder"
        printUsage && exit 1;
    fi
elif [ "$scmd" = "stop" ] || [ "$scmd" = "status" ]; then
    if [ $# -gt 1 ]; then
        echo "ERROR: more parameters are given. Only one required."
        printUsage && exit 1;
    fi
else
    printUsage && exit 1;
fi

## Running commands
if [ "$scmd" = "start" ]; then
    PID=$$ && echo $PID > "/tmp/traffic-logger.pid"
    echo "Running main script with PID=$PID..."
    start
elif [ "$scmd" = "status" ]; then
    status
elif [ "$scmd" = "stop" ]; then
    stop
fi

exit 0;
