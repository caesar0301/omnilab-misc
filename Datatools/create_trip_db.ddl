CREATE TABLE IF NOT EXISTS trip_data (
  medallion varchar(64),
  hack_license varchar(64),
  vendor_id varchar(64),
  rate_code int,
  store_and_fwd_flag varchar(64),
  pickup_datetime timestamp,
  dropoff_datetime timestamp,
  passenger_count smallint,
  trip_time_in_secs int,
  trip_distance double,
  pickup_longitude double,
  pickup_latitude double,
  dropoff_longitude double,
  dropoff_latitude double
  ) ROW FORMAT
  DELIMITED FIELDS
  TERMINATED BY ','
  STORED AS TEXTFILE;

CREATE TABLE IF NOT EXISTS trip_fare_data (
  medallion varchar(64), 
  hack_license varchar(64), 
  vendor_id varchar(64), 
  pickup_datetime timestamp, 
  payment_type varchar(32), 
  fare_amount double, 
  surcharge double, 
  mta_tax double, 
  tip_amount double, 
  tolls_amount double, 
  total_amount double 
  ) ROW FORMAT DELIMITED FIELDS TERMINATED BY ',' 
  STORED AS TEXTFILE;
  
LOAD DATA INPATH "trip_data" INTO TABLE trip_data;
LOAD DATA INPATH "trip_fare_data" INTO TABLE trip_fare_data;
