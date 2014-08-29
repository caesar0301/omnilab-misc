/* example to show how to use avro storage in pig. */

-- Author Xiaming Chen
-- chenxm35@gmail.com

/* register piggybank package which is compiled againist 
hadoop 0.23.x/2.0.x release by passing option
-Dhadoopversion=23 to ant when compiling piggybank.jar.
*/
REGISTER ./piggybank-23.jar

/* needed to parse schema by piggybank. */
REGISTER ./json-simple-1.1.1.jar

/* simplify method call prefix */
DEFINE AvroStorage org.apache.pig.piggybank.storage.avro.AvroStorage;

/* load flows from sample file. */
flows = load 'sample-small.avro' using  AvroStorage();

/* filter out invalid flows with lost fields. */
filtered = filter flows by srcTotPkts is not null and dstTotPkts is not null and assocApName is not null;

/* group flows by AP name */
apgroup = group filtered by assocApName;

/* calculate traffic summary */
traffic = foreach apgroup generate $0 as ap, SUM(filtered.srcTotPkts) as uptraffic, SUM(filtered.dstTotPkts) as downtraffic;

/* store data to text file */
STORE traffic INTO 'pig-avro-example.out' USING PigStorage();
