SET debug off;
SET job.name 'Read and write files';
SET parquet.compression gzip;

a = LOAD '$input' USING PigStorage();
STORE a INTO '$output' USING PigStorage();
