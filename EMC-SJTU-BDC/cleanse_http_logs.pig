
/*
Preprocess HTTP logs to EMC data challenge.

@Author: Xiaming Chen - chenxm35@gmail.com
*/

-- for debugging
-- %declare input 'justniffer.dat'
-- %declare output 'http_logs_clean.out'

SET debug off;
SET job.name 'Cleansing HTTP';
SET parquet.compression gzip;
SET log4j.logger.org.apache.hadoop error;

DEFINE Sessionize datafu.pig.sessions.Sessionize('5m');
DEFINE GenUUIDRand com.piggybox.uuid.GenUUIDRand();
DEFINE StripUrl com.piggybox.http.StripUrl;
DEFINE TopPrivateDomain com.piggybox.http.TopPrivateDomain;
DEFINE MobileType com.piggybox.http.MobileType;
DEFINE ServiceCategoryClassify com.piggybox.http.ServiceCategoryClassify;
DEFINE UnixToISO org.apache.pig.piggybank.evaluation.datetime.convert.UnixToISO();
DEFINE CountEachFlatten datafu.pig.bags.CountEach('flatten');
DEFINE SumEachBy com.piggybox.bags.SumEachBy;
DEFINE MergeTuples com.piggybox.bags.MergeTuples;
DEFINE NthTupleFromBag com.piggybox.bags.NthTupleFromBag;
DEFINE UserAgentClassify datafu.pig.urls.UserAgentClassify;
DEFINE AppendToBag datafu.pig.bags.AppendToBag;

-- read raw HTTP logs output by justniffer
DEFINE M_LOAD_RAW_HTTP(input_file) RETURNS data {
	$data = LOAD '$input_file' USING
	com.piggybox.loader.STLRegex('\\"\\s\\"') as (
		time_fields: chararray,
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
		response_keep_alive:chararray
		);

	$data = FOREACH $data {
		chops = STRSPLIT(time_fields, ' ');
		source_ip = (chararray)chops.$0;
		-- source port
		sport = REGEX_EXTRACT(chops.$1, '(\\d+)', 1);
		source_port = (sport is null ? -1 : (int)sport);
		dest_ip = (chararray) chops.$2;
		-- dest port
		dport = REGEX_EXTRACT(chops.$3, '(\\d+)', 1);
		dest_port = (dport is null ? -1 : (int)dport);
		-- connection info
		conn = (chararray) chops.$4;
		time_pattern = '(\\d+\\.?\\d*)';
		conn_ts = REGEX_EXTRACT(chops.$5, time_pattern, 1);
		conn_ts = (conn_ts is null ? -1 : (double)conn_ts);
		close_ts = REGEX_EXTRACT(chops.$6, time_pattern, 1);
		close_ts = (close_ts is null ? -1 : (double)close_ts);
		conn_dur = REGEX_EXTRACT(chops.$7, time_pattern, 1);
		conn_dur = (conn_dur is null ? -1 : (double)conn_dur);
		idle_time0 = REGEX_EXTRACT(chops.$8, time_pattern, 1);
		idle_time0 = (idle_time0 is null ? -1 : (double)idle_time0);
		request_ts = REGEX_EXTRACT(chops.$9, time_pattern, 1);
		request_ts = (request_ts is null ? -1 : (double)request_ts);
		request_dur = REGEX_EXTRACT(chops.$10, time_pattern, 1);
		request_dur = (request_dur is null ? -1 : (double)request_dur);
		response_ts = REGEX_EXTRACT(chops.$11, time_pattern, 1);
		response_ts = (response_ts is null ? -1 : (double)response_ts);
		response_dur_b = REGEX_EXTRACT(chops.$12, time_pattern, 1);
		response_dur_b = (response_dur_b is null ? -1 : (double)response_dur_b);
		response_dur_e = REGEX_EXTRACT(chops.$13, time_pattern, 1);
		response_dur_e = (response_dur_e is null ? -1 : (double)response_dur_e);
		idle_time1 = REGEX_EXTRACT(chops.$14, time_pattern, 1);
		idle_time1 = (idle_time1 is null ? -1 : (double)idle_time1);
		request_size = REGEX_EXTRACT(chops.$15, '(\\d+)', 1);
		request_size = (request_size is null ? -1 : (int)request_size);
		response_size = REGEX_EXTRACT(chops.$16, '(\\d+)', 1);
		response_size = (response_size is null ? -1 : (int)response_size);
		request_method = REPLACE(chops.$17, '\\"', '');
		GENERATE
			source_ip as source_ip:chararray,
			source_port as source_port:int,
			dest_ip as dest_ip:chararray,
			dest_port as dest_port:int,
			conn as conn:chararray,
			conn_ts as conn_ts:double,
			close_ts as close_ts:double,
			conn_dur as conn_dur:double,
			idle_time0 as idle_time0:double,
			request_ts as request_ts:double,
			request_dur as request_dur:double,
			response_ts as response_ts:double,
			response_dur_b as response_dur_b:double,
			response_dur_e as response_dur_e:double,
			idle_time1 as idle_time1:double,
			request_size as request_size:int,
			response_size as response_size:int,
			request_method as request_method:chararray,
			request_url ..;
	};

	$data = FILTER $data BY source_port != -1 and dest_port != -1 and request_ts != -1 and request_method is not null;
};

raw_logs = M_LOAD_RAW_HTTP('$input');

-- select required fields in this BDC.
selected_logs = FOREACH raw_logs GENERATE
	source_ip as ip: chararray,
	(long)(request_ts * 1000) as stime: long, -- milliseconds
	(long)((response_ts + response_dur_e) * 1000) as etime: long, -- milliseconds
	request_size + response_size as size: long,
	(request_url == 'N/A' ? '' : request_url) as url: chararray,
	(request_host == 'N/A' ? '' : request_host) as host: chararray,
	(request_user_agent == 'N/A' ? '' : request_user_agent) as user_agent: chararray,
	(request_referrer == 'N/A' ? '' : request_referrer) as referrer: chararray;
selected_logs = FILTER selected_logs BY stime is not null;

-- add additional fields
extended = FOREACH selected_logs GENERATE
	UnixToISO(stime) as isotime: chararray,
	ip, stime, etime, size,
	host,
	StripUrl(url) as url,
	TopPrivateDomain(host) as tld: chararray,
	MobileType(user_agent) as mobile: chararray,
	FLATTEN(ServiceCategoryClassify(host)) as (SP:chararray, SCAT:chararray, SCAT1: int);

-- sessonize individual's logs
ugroups = GROUP extended by ip;
sessionized = FOREACH ugroups {
	ordered = ORDER extended BY isotime;
	GENERATE FLATTEN(Sessionize(ordered)) as (isotime,
		ip, stime, etime, size, host, url, tld, mobile, SP, SCAT, SCAT1, session_id);
}
sessionized = FOREACH sessionized GENERATE ip .. session_id;

-- generate session statistics
sgroups = GROUP sessionized BY (ip, session_id);
sessions = FOREACH sgroups {
	-- order by time
	sessionized = ORDER sessionized BY stime;
	total_bytes = SUM(sessionized.size);
	total_requests = COUNT(sessionized);
	-- summarize a session
	sstime = MIN(sessionized.stime);
	setime = MAX(sessionized.etime);
	-- mobile operating system
	-- mobos = FOREACH sessionized GENERATE mobile;
	-- mobile = TopDesc(1, 1, CountEachFlatten(mobos));
	-- sum up traffic volumn for each service provider
	sp_traffic = FOREACH sessionized GENERATE TOTUPLE(SP, SCAT, tld), size;
	topsp = TOP(1, 1, SumEachBy(sp_traffic, 0, 1));
	topsp0 = NthTupleFromBag(0, topsp, TOTUPLE(null, null));
	-- sum up total requests for each service provider
	-- toprqt = TOP(1, 1, CountEachFlatten(sp_traffic.$0));
	-- toprqt0 = NthTupleFromBag(0, toprqt, TOTUPLE(null, null));
	GENERATE group.$0 as ip: chararray,
		sstime as sstime: long,
		setime as setime: long,
		total_requests as total_requests: long,
		total_bytes as total_bytes: long,
		FLATTEN(topsp0) as (service:chararray, bytes:long);
}
sessions = FOREACH sessions GENERATE ip, sstime, setime, total_requests, total_bytes,
	FLATTEN(service), bytes;
sessions = FILTER sessions BY setime > 0 and setime >= sstime;
sessions = ORDER sessions BY ip, sstime;

-- save to file systems
STORE sessions INTO '$output' USING PigStorage(',');