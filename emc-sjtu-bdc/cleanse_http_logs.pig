
/*
Preprocess HTTP logs to EMC data challenge.

@Author: Xiaming Chen - chenxm35@gmail.com
*/

-- for debugging
%declare input '20141002-1400.jn.out.gz'
%declare output 'output'

DEFINE Sessionize datafu.pig.sessions.Sessionize('5m');
DEFINE GenUUIDRand com.piggybox.uuid.GenUUIDRand();

SET debug off
SET job.name 'Cleansing HTTP'

-- read raw HTTP logs output by justniffer
DEFINE M_LOAD_RAW_HTTP(input_file) RETURNS data {
	$data = LOAD '$input_file' USING PigStorage('\t') as (
		source_ip:chararray,
		source_port:int,
		dest_ip:chararray,
		dest_port:int,
		conn:chararray,
		conn_ts:double,
		close_ts:double,
		conn_dur:double,
		idle_time0:double,
		request_ts:double,
		request_dur:double,
		response_ts:double,
		response_dur_b:double,
		response_dur_e:double,
		idle_time1:double,
		request_size:int,
		response_size:int,
		request_method:chararray,
		request_url:chararray,
		request_protocol:chararray,
		request_host:chararray,
		request_user_agent:chararray,
		request_referrer:chararray,
		request_conn:chararray,
		request_keep_alive:chararray,
		response_protocol:chararray,
		response_code:chararray,
		response_server:chararray,
		response_clen:chararray,
		response_ctype:chararray,
		response_cenc:chararray,
		response_etag:chararray,
		response_cache_ctl:chararray,
		response_last_mod:chararray,
		response_age:chararray,
		response_expire:chararray,
		response_conn:chararray,
		response_keep_alive:chararray);
};

raw_logs = M_LOAD_RAW_HTTP('$input');

selected_logs = FOREACH raw_logs GENERATE
	source_ip,
	request_ts,
	response_ts + response_dur_e AS response_ts_e,
	request_size + response_size AS size,
	request_url,
	request_host,
	request_user_agent,
	request_referrer,
	GenUUIDRand AS httpid;

DESCRIBE selected_logs;