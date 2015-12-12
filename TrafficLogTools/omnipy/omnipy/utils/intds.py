import os
import tldextract

__author__ = 'chenxm'
__all__ = ["IDS"]

class IDS(object):
    '''
    Python module to access Internet domain suffixes data.
    '''
    def __init__(self):
        this_dir, this_file = os.path.split(__file__)
        yamlfile = os.path.join(this_dir, "..", "..", "intds.yaml")
        self.ids = yaml.load(open(yamlfile))['ids']

    def database(self):
        return self.ids

    def tld_info(self, tld):
        info = "unknown"
        if tld is not None and len(tld) > 0:
            tld = tld.strip(".").rsplit(".", 1)[-1]
            if tld in self.ids:
                info = self.ids[tld]
        return {'suffix': tld,
                'country': info}

    def host_info(self, url):
        tld = tldextract.extract(url)
        subdomain = tld.subdomain
        domain = tld.domain
        suffix = tld.suffix
        country = self.tld_info(suffix)['country']
        return {'subdomain': subdomain,
                'domain': domain,
                'suffix': suffix,
                'country': country}