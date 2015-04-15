
/*
Preprocess HTTP logs to EMC data challenge.

@Author: Xiaming Chen - chenxm35@gmail.com
*/

-- for debugging
-- %declare input 'justniffer.dat'
-- %declare output 'http_logs_clean.out'

SET debug off;
SET job.name 'Cleansing HTTP for EMCBDC2015';
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
		GENERATE
			chops.$0 as source_ip:chararray,
			chops.$1 as source_port:chararray,
			chops.$2 as dest_ip:chararray,
			chops.$3 as dest_port:chararray,
			chops.$4 as conn:chararray,
			chops.$5 as conn_ts:chararray,
			chops.$6 as close_ts:chararray,
			chops.$7 as conn_dur:chararray,
			chops.$8 as idle_time0:chararray,
			chops.$9 as request_ts:chararray,
			chops.$10 as request_dur:chararray,
			chops.$11 as response_ts:chararray,
			chops.$12 as response_dur_b:chararray,
			chops.$13 as response_dur_e:chararray,
			chops.$14 as idle_time1:chararray,
			chops.$15 as request_size:chararray,
			chops.$16 as response_size:chararray,
			chops.$17 as request_method:chararray,
			request_url ..;
	};

	$data = FILTER $data BY source_port != 'N/A' and request_ts != 'N/A'
		and response_ts != 'N/A' and response_dur_b != 'N/A'
		and response_dur_e != 'N/A' and request_size != 'N/A'
		and response_size != 'N/A';
};

raw_logs = M_LOAD_RAW_HTTP('$input');

-- select required fields in this BDC.
selected_logs = FOREACH raw_logs {
	time_pattern = '(\\d+\\.?\\d*)';
	source_port = REGEX_EXTRACT(source_port, '(\\d+)', 1);
	source_port = (source_port is null ? -1 : (int)source_port);
	request_ts = REGEX_EXTRACT(request_ts, time_pattern, 1);
	request_ts = (request_ts is null ? -1 : (long)request_ts);
	response_ts = REGEX_EXTRACT(response_ts, time_pattern, 1);
	response_ts = (response_ts is null ? -1 : (long)response_ts);
	request_size = (long)request_size;
	response_size = (long)response_size;
	request_host = (request_host == 'N/A' ? null : request_host);
	request_url = (request_url == 'N/A' ? null : StripUrl(request_url));
	request_user_agent = (request_user_agent == 'N/A' ? null : request_user_agent);
	request_referrer = (request_referrer == 'N/A' ? null : request_referrer);
	GENERATE
		source_ip as ip:chararray,
		source_port as sport: int,
		(request_ts * 1000) as stime: long, -- milliseconds
		(long)((response_ts + (double)response_dur_e) * 1000) as etime: long,
		(request_size + response_size) as size: long,
		request_host as host: chararray,
		request_url as url: chararray,
		request_user_agent as user_agent: chararray,
		request_referrer as referrer: chararray;
}
selected_logs = FILTER selected_logs BY sport > 0 and stime > 0 and etime > 0
	and size >= 0 and host is not null;

-- add additional fields
extended = FOREACH selected_logs GENERATE
	UnixToISO(stime) as isotime: chararray,
	ip, stime, etime, size, host, url,
	MobileType(user_agent) as mobile: chararray,
	TopPrivateDomain(host) as tld: chararray,
	FLATTEN(ServiceCategoryClassify(host)) as (SP:chararray, SCAT:chararray, SCAT1: int);

-- sessonize individual's logs
ugroups = GROUP extended BY ip;
sessionized = FOREACH ugroups {
	ordered = ORDER extended BY stime;
	GENERATE FLATTEN(Sessionize(ordered));
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
