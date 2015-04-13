CREATE TABLE IF NOT EXISTS d4d_mov_site (
  user_id int,
  time timestamp,
  loc int
  ) ROW FORMAT
  DELIMITED FIELDS
  TERMINATED BY ','
  STORED AS TEXTFILE;

CREATE TABLE IF NOT EXISTS d4d_mov_arr (
  user_id int,
  time timestamp,
  loc int
  ) ROW FORMAT
  DELIMITED FIELDS
  TERMINATED BY ','
  STORED AS TEXTFILE;
  
LOAD DATA INPATH "/user/chenxm/D4D/SET2-M" INTO TABLE d4d_mov_site;
LOAD DATA INPATH "/user/chenxm/D4D/SET3-M" INTO TABLE d4d_mov_arr;
