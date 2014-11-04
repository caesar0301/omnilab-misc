update t_lable_group_comp
set format_content = REPLACE(REPLACE(format_content, '\r', ''), '\n', ' ');

select * from t_lable_group_comp INTO OUTFILE "t_lable_group_comp" FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '"' ESCAPED BY '\\' LINES TERMINATED BY '\r\n';