#!/usr/bin/python
__author__ = 'chenxm'
__email__ = 'chenxm35@gmail.com'

import sys, os
import urllib2

import html5lib
import html5lib.treebuilders as tb

prefix = "http://ip-science.thomsonreuters.com/cgi-bin/jrnlst/jlresults.cgi?PC=D&mode=print&Page="

def _valid_XML_char_ordinal(i):
    return (# conditions ordered by presumed frequency
        0x20 <= i <= 0xD7FF
        or i in (0x9, 0xA, 0xD)
        or 0xE000 <= i <= 0xFFFD
        or 0x10000 <= i <= 0x10FFFF
    )

def request_page(url):
    ''' Request html page of given URL
    '''
    print("Requesting %s" % url)
    filetypes = []
    wholepage = urllib2.urlopen(url).read()
    if wholepage == None:
        return filetypes
    parser = html5lib.HTMLParser(tree = tb.getTreeBuilder("lxml"))
    try:
        html_doc = parser.parse(wholepage)
    except ValueError:
        wholepage_clean = ''.join(c for c in wholepage
                                  if _valid_XML_char_ordinal(ord(c)))
        html_doc = parser.parse(wholepage_clean)
    return html_doc

def parse_html(url):
    """ Parse page content
    """
    html_doc = request_page(url)
    data_list = html_doc.find('//{*}dl')
    i = 0
    res = []
    for item in data_list:
        if i % 3 == 0: # DT
            name = item.find('./{*}strong').text
            issn = item.tail
        elif i % 3 == 1: # BR
            pass
        elif i % 3 == 2: # DT
            press = item.text
        i += 1
        if i % 3 == 0:
            name = name.strip('\r\n ')
            issn = issn.strip('\r\n ')
            press = issn.strip('\r\n ')
            # record = ';;'.join([name, issn, press])
            record = ' << '.join([name, issn])
            print(record)
            res.append(record)
            name = None
            issn = None
            press = None
    return res

def dump(result, output):
    ofile = open(output, 'wb')
    for record in result:
        ofile.write(record + '\n')
    ofile.close()

if __name__ == "__main__":
    res = []
    for i in range(1, 19):
        url = prefix + str(i)
        res.extend(parse_html(url))
    dump(res, 'sci.txt')
