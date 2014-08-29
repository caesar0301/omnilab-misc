#!/usr/bin/env python
# The Activity-Entity model for mobile HTTP records
#
# By chenxm
#
import zlib

from tldextract import TLDExtract

from PyOmniMisc.traffic.http import HTTPLogEntry
from PyOmniMisc.utils.web import URL
from webtree import WebTree, WebNode


def _crc32(string):
    return zlib.crc32(string) & 0xffffffff


def _format_entity(e):
    ''' Format the entity in a readable way
    '''
    return "%s:%d-->%s:%d | %s | %s | %s | %s | %s | %s | %s (%s)" % ( \
        e['source_ip'], e['source_port'],
        e['dest_ip'], e['dest_port'],
        e.rqtstart(), e.rspend(),
        e.method(),
        e.url()[:60],
        e.code(),
        e.type(),
        e.rspsize(),
        e['response_content_length'])

_DUR_LOW_BOUND = 0.1 # sec, a lower-bound duration

def _overlap(E1, E2):
    ''' Get the overlaped time duration of two entities
    Return overlapped duration: <0, =0, or >0
    '''
    s1 = E1.rqtstart()
    e1 = E1.rspend()
    s2 = E2.rqtstart()
    e2 = E2.rspend()
    #print (s1, e1), (s2,e2)
    if None in [s1, s2]:
        return None
    if e1 is None: e1 = s1 + _DUR_LOW_BOUND
    if e2 is None: e2 = s2 + _DUR_LOW_BOUND
    if s2 >= s1:
        return min(e1, e2) - s2
    else:
        return min(e1, e2) - s1

def _head_diff(E1, E2):
    s1 = E1.rqtstart()
    s2 = E2.rqtstart()
    if None in [s1, s2]:
        return None
    return abs(s1-s2)

def _tail_diff(E1, E2):
    s1 = E1.rqtstart()
    e1 = E1.rspend()
    s2 = E2.rqtstart()
    e2 = E2.rspend()
    #print (s1, e1), (s2,e2)
    if None in [s1, s2]:
        return None
    if e1 is None: e1 = s1 + _DUR_LOW_BOUND
    if e2 is None: e2 = s2 + _DUR_LOW_BOUND
    return abs(e1-e2)

def _domain1st(url):
    if url is None:
        return None
    try:
        ex = TLDExtract(suffix_list_url=None) # disable live
    except:
        ex = TLDExtract()
    subdomain, domain, suffix = ex(url)
    return '.'.join([domain,suffix])

def _is_pred_entity(E): # improve the quality
    if 'text' in str(E.type()):
        return True
    return False


class AEM(object):
    C_UNCL = 9 # unclassified
    C_CONJ = 1 # conjunction
    C_PRLL = 2 # parallel
    C_RLYD = 3 # relayed
    C_SRAL = 4 # serial
    _USER_READING_TIME = 5
    _SESSION_TIMEOUT = 60     # 60 sec
    _CONJ_ST_DIFF = 0.5        # sec, |ts1-ts2| < 0.5
    _CONJ_ET_PCRT = 0.1     # 10%, |te1-te2|/min(t1,t2) < 0.1
    _RLYD_TDIFF1 = 0         # ts2-te1 >= 0
    _RLYD_TDIFF2 = 1         # sec, ts2-te1 < 0.1
    _RLYD_FS = 768*1024            # Byte, file size threshold
    _SRAL_TDIFF1 = 0         # sec, ts2-te1 > 0
    _SRAL_TDIFF2 = 10         # sec, ts2-te1 <= 10
    _PRLL_OL = 0             # sec, overlap
    _CUT_TIMEOUT = 3        # sec, time gap between user clickes (or user's reading time)
    _PAGE_FAT = 5             # nubmer of embedded entities of fat page
    _PAGE_SLIM = 2            # number of embedded entities of slim page

    def __init__(self, http_entries, gap=_CUT_TIMEOUT):
        assert isinstance(http_entries[0], HTTPLogEntry)
        # sort by request time
        http_entries.sort(key=lambda x:x.rqtstart())
        self._entities = [e for e in http_entries if e.rqtstart()!=None]
        self._ss = dict() # sessions for valid user agent
        self._nss = dict() # sessions as ua is None
        self._gap = gap
        for e in self._entities:
            ua = e.ua()
            if ua is not None:
                if ua not in self._ss:
                    self._ss[ua] = [-1]
                ss = self._ss[ua]
                lt = ss[0] # -1 or timestamp
                rs = e.rqtstart()
                if rs - lt > self._SESSION_TIMEOUT:
                    ss.append([e]) # a new session
                else:
                    ss[-1].append(e) # append to last session
                # set new last entity time
                ss[0] = rs 
            else:
                domain = _domain1st(e.host())
                if domain not in self._nss:
                    self._nss[domain] = [-1]
                nss = self._nss[domain]
                lt = nss[0]
                rs = e.rqtstart()
                if rs - lt > self._SESSION_TIMEOUT:
                    nss.append([e])
                else:
                    nss[-1].append(e)
                nss[0] = rs

    def sessionsWithUA(self):
        return self._ss

    def sessionsWithoutUA(self):
        return self._nss

    def _is_relayed(self, E1, E2):
        ol = _overlap(E1, E2)
        if ol is None: return None
        # sdm1 = _domain1st(E1.host())
        # sdm2 = _domain1st(E2.host())
        if ol <= self._RLYD_TDIFF1 and \
            abs(ol) < self._RLYD_TDIFF2:
            return True
        return False

    def _is_serial(self, E1, E2):
        # if _is_relayed(E1, E2):
        #     return False
        ol = _overlap(E1, E2)
        if ol is None: return None
        if ol <= self._SRAL_TDIFF1 and abs(ol) < self._SRAL_TDIFF2:
            return True
        return False

    def _is_conj(self, E1, E2):
        ''' Three contraints:
        1. head_diff <= 0.5 sec
        2. the same subdomain, e.g., f.b.com ~ g.b.com
        3. tail_diff meets duration portion ~ 10%
        '''
        hd = _head_diff(E1, E2)
        td = _tail_diff(E1, E2)
        if None in [hd, td]:
            return None
        dur = E1.dur()
        d1 = dur if dur else _DUR_LOW_BOUND
        dur = E2.dur()
        d2 = dur if dur else _DUR_LOW_BOUND
        sdm1 = _domain1st(E1.host())
        sdm2 = _domain1st(E2.host())
        if hd <= self._CONJ_ST_DIFF and \
            float(td)/min(d1, d2) < self._CONJ_ET_PCRT and \
            sdm1 == sdm2:
            return True
        return False

    def _is_parallel(self, E1, E2):
        # if _is_conj(E1, E2):
        #     return False
        ol = _overlap(E1, E2)
        if ol is None: return None
        if ol > self._PRLL_OL:
            return True
        return False

    def classify(self, E1, E2):
        ''' Classify entities in a session
        '''
        t = self.C_UNCL
        if self._is_conj(E1, E2):
            t = self.C_CONJ
        elif self._is_parallel(E1, E2):
            t = self.C_PRLL
        elif self._is_relayed(E1, E2):
            t = self.C_RLYD
        elif self._is_serial(E1, E2):
            t = self.C_SRAL
        return t

    def model(self, entities):
        ''' Model activities based on emperical rules:
        For entities with Referrer:

        Without referrer:
        '''
        wts = []
        entities.sort(cmp=lambda x,y:cmp(x,y),key=lambda x: x.rqtstart())
        last = None
        for e in entities:
            nn = WebNode(e) # create a new node
            nn_ref = nn.pl.referer()
            nn_st = nn.pl.rqtstart()
            if nn_st == None: # it's not a valid HTTP request
                continue
            cut = False
            linked_flag = False

            if last is None:
                cut = True
            else:
                nn.aem_last = self.classify(last.pl, nn.pl)
                if nn.aem_last == self.C_UNCL:    # force break with long scilence
                    cut = True
                else:
                    # Check based on referrer
                    if nn_ref != None: # with referrer
                        nst = set() # list of new subtrees
                        for wt in wts[::-1]:
                            un_map = {} # create map between URL and node id for speed-up
                            for node in wt.sorted_nodes():
                                url = node.pl.url()
                                if url == None: continue
                                #url = URL.strip_proto(URL.strip_param(url)) # strip proto and params
                                url = URL.strip_proto(url)
                                un_map[url] = node.identifier
                            # Find its predecessor
                            #nn_ref = URL.strip_proto(URL.strip_param(nn_ref)) # strip proto and params
                            nn_ref = URL.strip_proto(nn_ref)
                            pred_id = un_map.get(nn_ref)
                            if pred_id != None: # Predecessor found...
                                wt.add_node(nn, pred_id)
                                linked_flag = True

                                nn.aem_last = self.classify(last.pl, nn.pl)
                                nn.aem_pred = self.classify(wt[pred_id].pl, nn.pl)
                                nn.fake_link = False
                                nn.tag = nn.gen_tag() # update tag

                                pch = len(wt.is_branch(pred_id))
                                is_pred = _is_pred_entity(wt[pred_id].pl)
                                is_root = (pred_id==wt.root or wt[pred_id].fake_link)
                                if (not is_root) and (nn.aem_last==self.C_SRAL and is_pred and pch>=self._PAGE_SLIM):
                                    nst.add(pred_id) # then remenber to remove this subtree
                                if (not is_root) and (is_pred and pch >= self._PAGE_FAT):
                                    nst.add(pred_id)
                                if (not is_root) and (nn.aem_pred==self.C_UNCL and is_pred and pch>=self._PAGE_SLIM):
                                    nst.add(pred_id)
                                break
                        # cut down new subtrees
                        for pid in nst:
                            st = wt.remove_subtree(pid) # TODO: guess a bug here; the pid may not exist in this tree.
                            st = WebTree(st) # cast to WebTree
                            wts.append(st)
                    else: # without referrer
                        if nn.aem_last == self.C_SRAL and abs(_overlap(last.pl, nn.pl)) >= self._gap: # sec
                            cut = True
                        else: # create a fake link to its preceeder.
                            for wt in wts[::-1]:
                                if wt.contains(last.identifier):
                                    wt.add_node(nn, last.identifier)
                                    nn.aem_pred = nn.aem_last
                                    nn.fake_link = True
                                    nn.tag = nn.gen_tag() # set new tag
                                    linked_flag = True
                                    break
            # Create a new tree if it not linked to any tree
            if cut or (not linked_flag):
                nt = WebTree()
                if nn_ref != None: # a new process, create a dummy node to replace lost one
                    dn = WebNode(HTTPLogEntry())
                    dn._dummy = 1    # dummy flag
                    dn.pl['request_timestamp'] = nn.pl.rqtstart() # set start time
                    nn_ref = URL.strip_proto(nn_ref)
                    chops = nn_ref.split('/', 1)
                    dn.pl['request_host'] = chops[0]
                    if len(chops) == 1:
                        dn.pl['request_url'] = ''
                    else:
                        dn.pl['request_url'] = '/' + chops[1]
                    dn.tag = "(dummy) %s | %s" % (dn.pl.rqtstart(), dn.pl.url()[:50]) # also fake
                    nt.add_node(dn, parent=None)
                    nt.add_node(nn, dn.identifier)
                else:
                    nt.add_node(nn, parent=None)
                wts.append(nt)
            last = nn
        return wts



if __name__ == '__main__':
    from PyOmniMisc.traffic.http import HTTPLogReader
    
    es = []
    for e in HTTPLogReader('../test/http_logs'):
        if e is not None: es.append(e)

    e1 = es[1]
    e2 = es[2]
    print _overlap(e1,e2)
    print _head_diff(e1, e2)
    print _tail_diff(e1, e2)
    print _domain1st(e1.url())

    aem  = AEM(es)
    print 'conj:', aem._is_conj(e1, e2)
    print 'parr:', aem._is_parallel(e1, e2)
    print 'rely:', aem._is_relayed(e1, e2)
    print 'serl:', aem._is_serial(e1, e2)
    
    for ua in aem._ss:
        ss = aem._ss[ua]
        print '\n******************'
        print ua
        for el in ss[1:]:
            trees = aem.model(el)
            for wt in trees:
                print('')
                wt.show(key=lambda x: x.pl.rqtstart(), reverse=False)