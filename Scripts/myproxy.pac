function FindProxyForURL(url, host) {
    var proxyserver = 'jackfan.com:4000';

    var proxyBypassPatterns = new Array(
        // Domestic
        "*baidu.com",
        "*.cn",
        "*.dp",
        "*.hsiamin.com",
        "*alipay.com",
        "*alipay.com",
        "*dianping.com",
        "*dianpingoa.com",
        "*github.com",
        "*qq.com",
        "*taobao.com",
        "localhost",
        "127.0.0.1",
        // Academic
        "*acm.org",
        "*aiaa.org",
        "*aps.org",
        "*arxiv.org",
        "*citeulike.org",
        "*computer.org",
        "*computer.org",
        "*cshlp.org",
        "*ieee.org",
        "*iiisci.org",
        "*iop.org",
        "*jstor.org",
        "*jstor.org",
        "*metapress.com",
        "*nature.com",
        "*nih.gov",
        "*nih.gov",
        "*pnas.org",
        "*projecteuclid.org",
        "*science.com",
        "*sciencedirect.com",
        "*sciencemag.org",
        "*sciencemag.org",
        "*siam.org",
        "*springer.com",
        "*tandfonline.com",
        "*wiley.com"
    );

    for(var i=0; i<proxyBypassPatterns.length; i++) {
        var value = proxyBypassPatterns[i];
        if ( localHostOrDomainIs(host, value) ) {
            return "DIRECT";
        }
    }
    return "PROXY " + proxyserver;
}
