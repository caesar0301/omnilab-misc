#!/usr/bin/python
__author__ = 'chenxm'
__email__ = 'chenxm35@gmail.com'

import sys, os
import urllib2

import html5lib
import html5lib.treebuilders as tb

prefix = "http://www.computerhope.com/jargon/num/domains.htm"

def _valid_XML_char_ordinal(i):
    ## As for the XML specification, valid chars must be in the range of
    ## Char ::= #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]
    ## [Ref] http://stackoverflow.com/questions/8733233/filtering-out-certain-bytes-in-python
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
    nodes = html_doc.findall(
        "//{*}table[@class='mtable']//{*}tr[@class='tcw']")
    res = []
    if len(nodes) > 0:
        for node in nodes:
            tcells = node.findall("./{*}td")
            suffix = ''.join([str(i) for i in tcells[0].itertext()
                            if i not in ['', ' ']]).strip(".")
            desp = ''.join([str(i) for i in tcells[1].itertext()
                            if i not in ['', ' ']])
            res.append((suffix, desp))
    return res

def dump2yaml(result, dbfile="intds.update.yaml"):
    ofile = open(dbfile, 'wb')
    ofile.write("%YAML 1.1\n")
    ofile.write("---\n")
    ofile.write("ids:\n")
    for r in result:
        ofile.write("    %s: %s\n" % (r[0], r[1]))
    ofile.close()

if __name__ == "__main__":
    dump2yaml(parse_html(prefix))
