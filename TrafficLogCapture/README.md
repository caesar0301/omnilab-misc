TrafficLogCapture
------------

A simple wrapper to Extracting TCP/HTTP parameters from Pcap files
in both offline and live modes. 

A simple pcap-workflow.sh is given to process a specific pcap file with 
different tools: tcptrace, tstat, justniffer, pcapDPI).

by chenxm

2013-03



Requirements
------------


Your systems should have tcptrace, tstat, justniffer installed and
their binary files called with $PATH variables (ex. /usr/bin).

tcptrace: http://www.tcptrace.org/

tstat: http://tstat.tlc.polito.it

justniffer: http://justniffer.sourceforge.net/

and latest version of pcapDPI: https://github.com/caesar0301/pcapDPI


Install
--------------

Run command to build and install tools required:

    ./build-all.sh

Tested on Ubuntu 12, 13, 14, 64bit version


Usage
------------

First, install tcptrace, tstat, and justniffer manully on your system.

Second, `cd` to project root folder, then run `build.sh` to setup the project
by installing "nDPI" and "pcapDPI" automatically.

Third, for live sniffering, modify `live/traffic_live_start.sh` regarding to your own
configuration, then excute command in terminal:

    ./live/traffic_live_start.sh <output_folder>

for processing offline pcap file, run command:

    ./offline/pcap-workflow.sh <pcapfile>

The logs generated locate in default folder `output`.

Happy coding ;)
