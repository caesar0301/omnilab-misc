CREATE TABLE IF NOT EXISTS eb_ads_monitor (
  uid varchar(16),
  uid_stable smallint,
  aid varchar(16),
  pid varchar(16),
  user_agent varchar(32),
  os varchar(32),
  lang varchar(16),
  ip varchar(16),
  time varchar(16),
  action varchar(8)
  ) ROW FORMAT DELIMITED FIELDS TERMINATED BY '^' STORED AS TEXTFILE;
  
CREATE TABLE IF NOT EXISTS eb_ads_transform (
  uid varchar(16),
  time varchar(16)
  ) ROW FORMAT DELIMITED FIELDS TERMINATED BY '^' STORED AS TEXTFILE;


LOAD DATA INPATH "bdc2014_consumers/train/monitorData" INTO TABLE eb_ads_monitor;
LOAD DATA INPATH "bdc2014_consumers/train/transformData" INTO TABLE eb_ads_transform;
