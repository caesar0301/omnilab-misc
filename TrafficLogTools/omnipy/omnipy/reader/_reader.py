"""
The basic module about log readers
"""
import os
import re

from ..utils.gzip2 import GzipFile

__author__ = 'chenxm'
__all__ = ["FileReader"]

class FileReader(object):

	@staticmethod
	def open_file(filename, mode='rb'):
		""" open plain or compressed file
		@return file handler
		"""
		parts = os.path.basename(filename).split('.')
		try:
			assert parts[-1] == 'gz'
			fh = GzipFile(mode=mode, filename = filename)
		except:
			fh = open(filename, mode)
		return fh


	@staticmethod
	def list_files(folder, regex_str=r'.', match=True):
		""" find all files under 'folder' with names matching 
		some reguler expression
		"""
		assert os.path.isdir(folder)
		all_files_path = []
		for root, dirs, files in os.walk(folder):
			for filename in files:
				if match and re.match(regex_str, filename, re.IGNORECASE):
					all_files_path.append(os.path.join(root, filename))
				elif not match and re.search(regex_str, filename, re.IGNORECASE):
					all_files_path.append(os.path.join(root, filename))
		return all_files_path

class LogEntry(object):

	def __init__(self):
		self.data = {}

	def get(self, property):
		try:
			return self[property]
		except KeyError:
			return None

	def set(self, property, value):
		self[property] = value

	def __getitem__(self, property):
		return self.data[property]

	def __setitem__(self, property, value):
		self.data[property] = value

	def __str__(self):
		return str(self.data)


class LogReader(object):

	def __init__(self, filename):
		self.filename = filename
		self.filehandler = FileReader.open_file(filename)

	def __iter__(self):
		return self

	def next(self):
		try:
			new_line = self.filehandler.next()
			return new_line
		except StopIteration:
			self.filehandler.close()
			raise StopIteration