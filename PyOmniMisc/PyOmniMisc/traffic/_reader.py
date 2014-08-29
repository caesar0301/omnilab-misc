"""
The basic module about log readers
"""
__author__ = 'chenxm'

from PyOmniMisc.utils.file import FileReader


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