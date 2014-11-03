WiFiLogFilter
===================

Author: Wenjuan Gong
05-2013

This is a tool to filter out useful message from Aruba syslog
for research purpose.

Several types of messages are retained including:
 * Auth/Deauth
 * Assoc/Deassoc
 * User authentication
 * IP allocation
 * IP recycle

The message content is matched and extracted using Regular expression.
It's easy to extend the message filter capability.


HOW TO USE
------------

This tool runs on Java 1.6+ and makes to be compiled with Maven.
As Java and Maven are installed, you can start with:

        $ cd wifilogfilter
        $ mvn clean && mvn package

Apps shipped with this package contains:

1. Remove Ping-Pong effect from original logs:

        $ java -cp wifilogfilter.jar sjtu.omnilab.bd.apps.PPEffectFilter -i [source] -o [destination]

2. Filter the information which is related to location information and IP information in the ArubaSyslog:

        $ java -cp wifilogfilter.jar sjtu.omnilab.bd.apps.SyslogFilter -i [source] -o [destination]

3. Separate the filtered logs (output of SyslogFilter.java) into individual users.

        $ java -cp wifilogfilter.jar sjtu.omnilab.bd.apps.SyslogSplitter -i [source] -o [destination]

4. One-step manipulation of step 3 and 4:

        $ java -cp wifilogfilter.jar sjtu.omnilab.bd.apps.SyslogSessionExtractor -i [source] -o [destination]

NOTICE
----------

To avoid Out of Memory error, -Xmx1G or other option should be add to java command;
You can also use export this option to enviroment using

        $ export _JAVA_OPTIONS="-Xmx1G"