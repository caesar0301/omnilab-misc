__author__ = 'chenxm'

import re


class URL(object):

	M_STRICT = 's'
	M_LOOSE = 'l'

	@staticmethod
	def strip_proto(url):
		""" Remove the prefix of url
		url: input url string
		"""
		url_regex = re.compile(r"^(\w+:?//)?(.*)$", re.IGNORECASE)
		url_match = url_regex.match(url)
		if url_match:
			url = url_match.group(2)
		return url

	@staticmethod
	def strip_param(url):
		url_regex = re.compile(r"^((\w+://)?([^&\?]+))\??", re.IGNORECASE)
		url_match = url_regex.match(url)
		if url_match:
			url = url_match.group(1)
		return url
	

	@staticmethod
	def search(t, urls):
		trul2 = URL.strip_proto(t)
		for url in urls:
			if trul2 == URL.strip_proto(url):
				return True
		return False


	@staticmethod
	def cmp(u1, u2, mode = M_STRICT):
		if mode == URL.M_STRICT:
			# compare with parameters
			if URL.strip_proto(u1) == URL.strip_proto(u2):
				return True
			return False
		elif mode == URL.M_LOOSE:
			# compare without parameters
			u1 = URL.strip_proto(URL.strip_param(u1))
			u2 = URL.strip_proto(URL.strip_param(u2))
			if u1 == u2:
				return True
			return False
			

if __name__ == '__main__':
	url1 = 'http://www.baidu.com/hello?123'
	url2 = 'http://www.baidu.com/hello?456'

	print URL.strip_proto(url1)
	print URL.strip_param(url1)
	print URL.search(url1, [url1, url2])
	print URL.cmp(url1, url2, URL.M_STRICT)
	print URL.cmp(url1, url2, URL.M_LOOSE)