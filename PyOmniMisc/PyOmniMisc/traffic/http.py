"""
The module to manipulate Justniffer logs.

Justniffer log example (two entries):
111.186.59.89 53792 111.13.87.17 80 unique 1368599790.969373 1368599791.118075 0.038677 0.000066 1368599791.19264 0.011148 1368599791.53173 0.033909 0.000000 0.064902 1369 303 "POST" "/interface/f/ttt/v3/wbpullad.php?platform=android&s=213a9afe&c=android&wm=5091_0008&ua=LGE-Nexus+4__weibo__3.5.1__android__android4.2.2&oldwm=4260_0001&from=1035195010&skin=default&size=480&i=dfde15e&lang=en_US" "HTTP/1.1" "wbapp.mobile.sina.cn" "Nexus 4_4.2.2_weibo_3.5.1_android" "N/A" "Keep-Alive" "N/A" "HTTP/1.1" "200" "nginx" "N/A" "text/html" "gzip" "N/A" "N/A" "N/A" "N/A" "N/A" "keep-alive" "N/A"
111.186.59.89 51779 121.194.0.143 80 unique 1368599792.193907 1368599792.985738 0.062516 0.000020 1368599792.256443 0.000000 1368599792.932328 0.583842 0.092043 0.053410 429 22057 "GET" "/2/statuses/friends_timeline?picsize=240&count=25&c=android&wm=5091_0008&from=1035195010&skin=default&i=dfde15e&fromlog=100011628918270&s=213a9afe&gsid=4uu737333NjR69pWF0zzb6PKS4m&ua=LGE-Nexus+4__weibo__3.5.1__android__android4.2.2&oldwm=4260_0001&v_p=3&uicode=10000001&list_id=1&lang=en_US" "HTTP/1.1" "api.weibo.cn" "Nexus 4_4.2.2_weibo_3.5.1_android" "N/A" "Keep-Alive" "N/A" "HTTP/1.1" "200" "Apache" "21749" "application/json;charset=UTF-8" "gzip" "N/A" "N/A" "N/A" "N/A" "N/A" "close" "N/A"
"""
__author__ = 'chenxm'

import sys, csv
from _reader import LogEntry, LogReader
from PyOmniMisc.utils.web import URL


_NA_STR = 'N/A'
_FIELDS = [
"source_ip",
"source_port",
"dest_ip",
"dest_port",
"connection",
"connection_timestamp",
"close_timestamp",
"connection_time",
"idle_time_0",	# idle time from connection establishment
"request_timestamp",
"request_time",	# from the first byte of request to the last byte
"response_timestamp",
"response_time_begin", # from the last byte of request to the fist byte of response
"response_time_end", # from the first byte of response to the last byte
"idle_time_1",	# idle time to flow termination
"request_size",
"response_size",
"request_method",
"request_url",
"request_protocol",
"request_host",
"request_user_agent",
"request_referer",
"request_connection",
"request_keep_alive",
"response_protocol",
"response_code",
"response_server",
"response_content_length",
"response_content_type",
"response_content_encoding",
"response_etag",
"response_cache_control",
"response_last_modified",
"response_age",
"response_expires",
"response_connection",
"response_keep_alive",
]


class HTTPLogEntry(LogEntry):

	def __init__(self):
		LogEntry.__init__(self)
		for key in _FIELDS:
			self[key] = None
			
	@staticmethod
	def all():
		""" Get all properties of HTTP log entry
		"""
		return _FIELDS

	def url(self):
		""" assemble URL from host and URI
		"""
		host = self.get("request_host")
		uri = self.get("request_url")
		if None in [host, uri]:
			return None
		if uri[0:4] == 'http':
			# some URIs contains full URL addresses
			return URL.strip_proto(uri)
		return host+uri

	def host(self):
		return self.get('request_host')

	def referer(self):
		return self.get('request_referer')

	def method(self):
		return self.get('request_method')

	def ua(self):
		return self.get('request_user_agent')

	def code(self):
		return self.get('response_code')

	def type(self):
		return self['response_content_type']

	def socket(self):
		""" Get the socket of this entry
		"""
		for item in ['source_ip', 'source_port', 'dest_ip', 'dest_port']:
			if self[item] is None:
				assert("Invalid HTTPLogEntry: %s can't be None" % item)
		source = (self['source_ip'], self['source_port'])
		dest = (self['dest_ip'], self['dest_port'])
		return (source, dest)

	def dur(self):
		'''
		Get elapsed seconds of this HTTP entry
		'''
		start = self.rqtstart()
		end = self.rspend()
		if not end:
			end = self.rqtend()
		if None not in [start, end]:
			return end-start
		return None

	def rqtstart(self):
		'''
		Get the start time of HTTP request
		'''
		return self['request_timestamp']

	def rqtend(self):
		'''
		Get the end time of HTTP request
		'''
		s = self['request_timestamp']
		e = self['request_time']
		if None in [s,e]:
			return None
		return s + e

	def rspstart(self):
		'''
		Get the start time of HTTP response
		'''
		return self['response_timestamp']

	def rspend(self):
		'''
		Get the end time of HTTP response
		'''
		s = self['response_timestamp']
		e = self['response_time_end']
		if None in [s,e]:
			return None
		return s + e

	def rqtsize(self):
		return self['request_size']

	def rspsize(self):
		return self['response_size']

	def __str__(self):
		return '%s:"%s:%s-->%s:%s %s %s %s"' % ( \
			'HTTPLogEntry',
			self['source_ip'], self['source_port'],
			self['dest_ip'], self['dest_port'],
			self.method(),
			self.rqtstart(),
			str(self.url())[:50])

	def __eq__(self, other):
		return self.rqtstart() == other.rqtstart() and \
		self.rspstart() == other.rspstart() and \
		self.url() == other.url()


def fft(time):
	'''
	Fix the float time stamp
	'''
	if '.' in time:
		p1, p2 = time.split('.')
		p1 = int(p1)
		if len(p2) <= 3:
			return p1 + int(p2)/1000.0
		elif len(p2) <= 6:
			return p1 + int(p2)/1000000.0
		elif len(p2) <= 9:
			return p1 + int(p2)/1000000000.0
	else:
		return int(time)


class HTTPLogReader(LogReader):

	def __init__(self, http_log_name, quiet = True):
		LogReader.__init__(self, http_log_name)
		self._csv_reader = csv.reader(self.filehandler, delimiter = ' ', quotechar = '\"', quoting=csv.QUOTE_MINIMAL)
		self._quiet = quiet


	def next(self):
		hle = None
		segments = []
		try:
			segments = self._csv_reader.next()
		except StopIteration:
			self.filehandler.close()
			raise StopIteration
		except csv.Error as e:
			if not self._quiet:
				print('WARNNING: file %s, line %d: %s' % (self.filename, self._csv_reader.line_num, e))

		if len(segments) == len(_FIELDS):
			hle = HTTPLogEntry()
			for i in range(0, len(_FIELDS)):
				value = (segments[i] if segments[i] != _NA_STR else None)
				hle[_FIELDS[i]] = value
			hle['source_port'] = int(hle['source_port'])
			hle['dest_port'] = int(hle['dest_port'])
			hle['connection_timestamp'] = fft(hle['connection_timestamp']) if hle['connection_timestamp'] else None
			hle['close_timestamp'] = fft(hle['close_timestamp']) if hle['close_timestamp'] else None
			hle['connection_time'] = fft(hle['connection_time']) if hle['connection_time'] else None
			hle['idle_time_0'] = fft(hle['idle_time_0']) if hle['idle_time_0'] else None
			hle['request_timestamp'] = fft(hle['request_timestamp']) if hle['request_timestamp'] else None
			hle['request_time'] = fft(hle['request_time']) if hle['request_time'] else None
			hle['response_timestamp'] = fft(hle['response_timestamp']) if hle['response_timestamp'] else None
			hle['response_time_begin'] = fft(hle['response_time_begin']) if hle['response_time_begin'] else None
			hle['response_time_end'] = fft(hle['response_time_end']) if hle['response_time_end'] else None
			hle['idle_time_1'] = fft(hle['idle_time_1']) if hle['idle_time_1'] else None
			hle['request_size'] = long(hle['request_size']) if hle['request_size'] else None
			hle['response_size'] = long(hle['response_size']) if hle['response_size'] else None

		# Manual splitting
		# try:
		# 	new_line = self.filehandler.next()
		# except StopIteration:
		# 	self.filehandler.close()
		# 	raise StopIteration
		# new_line = new_line.strip("\r \n")
		# if len(new_line) != 0:
		# 	hle = HTTPLogEntry()
		# 	segments = new_line.split(' ', 17)
		# 	try:
		# 		for i in range(0, 17):
		# 			value = segments[i].strip(' \t')
		# 			value = (value != _NA_STR and value or None)
		# 			hle[_FIELDS[i]] = value

		# 		parts = segments[17].strip().split(' "')
		# 		for j in range(0, len(_FIELDS) - 17):
		# 			value = parts[j].strip(' \"')
		# 			value = (value != _NA_STR and value or None)
		# 			hle[_FIELDS[ j+17 ]] = value
		# 	except IndexError:
		# 		hle = None

		return hle


if __name__ == '__main__':
	for f in HTTPLogEntry.all():
		print f
	reader = HTTPLogReader('../../test/http_logs')
	for e in reader:
		print e.url()
		print e.host()
		print e.referer()
		print e.method()
		print e.ua()
		print e.code()
		print e.type()
		print e.socket()
		print e.dur()
		print e.rqtstart()
		print e.rqtend()
		print e.rqtsize()
		print e.rspstart()
		print e.rspend()
		print e.rspsize()
		print e == e
		print e
	print fft('123456789.11')
	print fft('123456789.110')
	print fft('123456789.1101')
	print fft('123456789.11011')