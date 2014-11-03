ArubaLogUtils
===============

Series of tools/library to process wifi logs in OMNI-Lab, SJTU, China.
Note: These tools work on the original aruba wifi logs collected in our campus.


Usage
--------

* `syslogreplayer`:

  This is a simple tool to send UDP based log packets over network. It works
  for diagnoses of network condition or development test of logger software in
  lab environment.


* `wifilog-filter`:

  This maven project does some dirty work at the early stage of processing raw
  Aruba syslog.  Its funcitons include filtering each log entry from raw lines
  (SyslogFilter.java), splitting the daily logs into individual users
  (SyslogSplitter.java), extracting wifi sessions from user logs
  (SessionExtractor.java), and a simple one-step program
  (SplitterAndExtractor.java) to facilitate splitting and session extraction
  together.  Several workflows can be followed for different purposes:

  * [rawlogs] --> SyslogFilter.java --> [filteredlogs]

  * [filteredlogs] --> SplitterAndExtractor.java --> [sessions]


* `mark_session_ip.py`:

  This script works on the wifi sessions to mark each session with an allocated
  IP address.  `mark_batch.sh` helps to process multiple these session files in
  a batch mode. Workflow:

  * [sessions] --> mark_session_ip.py --> [ipsessions].



* `pure_movement.py`:

  This tools aims to generate pure movement information in wifi networks. This
  movement data can be used to study user mobility patterns in SJTU WiFi
  networks. Workflow:

  * [sessions] --> pure_movement.py --> [puremovement]



Contact
--------

Xiaming Chen, SJTU, China

chenxm35@gmail.com
