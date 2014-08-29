Hive-jdbc-example
==============

Configure hiveserver
-------------

Login to your hive cluster and start hiveserver:

    hive --service hiveserver

Copy the 'keyvalue.txt' in the package to your server's local path '/tmp/keyvalue.txt'

    scp keyvalue.txt you@hiveserver:/tmp/keyvalue.txt


Build example
--------------

You can run the example in eclipse as a mavan project or build it as a jar package:

    mvn package
    java -jar target/hive-jdbc-example-<version>.jar

Output
-----------

    Running: show tables 'testHiveDriverTable'
    testhivedrivertable
    Running: describe testHiveDriverTable
    key                     int                 
    value                   string              
    Running: load data local inpath '/tmp/a.txt' into table testHiveDriverTable
    Running: select * from testHiveDriverTable
    1    2
    2    3
    2    4
    Running: select count(*) from testHiveDriverTable
    3


Note
-----

source code from Internet