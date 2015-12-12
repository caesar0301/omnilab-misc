import os

from omnipy.reader import HTTPLogReader

def test_aem():
    es = []
    this_dir, this_file = os.path.split(__file__)
    testlog = os.path.join(this_dir, 'http_logs')
    for e in HTTPLogReader(testlog):
        if e is not None:
            es.append(e)
    if len(es) < 2:
    	return

    e1 = es[1]
    e2 = es[2]
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