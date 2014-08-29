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


HOW TO USE:

This tool runs on Java 1.6+ and makes to be compiled with Maven.
As Java and Maven are installed, you can start with:

        $cd wifilogfilter
        $mvn package

and use the tool with:

        $ java -jar ./target/wifilogfilter-<version>.jar

To avoid Out of Memory error, -Xmx1G or other option should be add to java command;
You can also use export this option to enviroment using

        $ export _JAVA_OPTIONS="-Xmx1G"