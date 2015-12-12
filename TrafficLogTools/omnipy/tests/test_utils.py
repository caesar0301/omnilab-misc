from omnipy.utils import FileType
from omnipy.utils import URL
from omnipy.utils import IDS
from omnipy.utils.stat import FMeasure, MSE, RMSE

def test_filetype():
    print FileType.detect_by_filename("hao123.com/a.html")

def test_stat():
    print FMeasure(0.5, 0.5)
    print MSE([1,1], [1,2])
    print RMSE([1,1], [1,2])

def test_url():
    url1 = 'http://www.baidu.com/hello?123'
    url2 = 'http://www.baidu.com/hello?456'

    print URL.strip_proto(url1)
    print URL.strip_param(url1)
    print URL.search(url1, [url1, url2])
    print URL.cmp(url1, url2, URL.M_STRICT)
    print URL.cmp(url1, url2, URL.M_LOOSE)

def test_ids():
    ids = IDS()
    print ids.tld_info(".edu.cn")
    print host_info("www.sjtu.edu.cn/index.html")