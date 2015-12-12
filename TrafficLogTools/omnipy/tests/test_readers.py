import os

from omnipy.reader import DPIMap
from omnipy.reader import HTTPLogEntry, HTTPLogReader
from omnipy.reader import TCPLogEntry
from omnipy.reader import LocationDB

def test_dpi_map():
    appcat = DPIMap()
    print appcat.protoName(0)
    print appcat.protoCat(0)
    print appcat.protoIDs("IM")
    print appcat.protoNames("IM")

def test_http_reader():
    for f in HTTPLogEntry.all():
        print f
    this_dir, this_file = os.path.split(__file__)
    reader = HTTPLogReader(os.path.join(this_dir, 'http_logs'))
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

def test_tcp_reader():
    print TCPLogEntry.all()

def test_wifi_reader():
    pass