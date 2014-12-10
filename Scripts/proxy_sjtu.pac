function isAcademicDomain(url, host){
    var domains = new Array(
        "acm.org",
        "aiaa.org",
        "aps.org",
        "arxiv.org",
        "citeulike.org",
        "computer.org",
        "cshlp.org",
        "ieee.org",
        "iiisci.org",
        "iop.org",
        "jstor.org",
        "metapress.com",
        "nature.com",
        "nih.gov",
        "pnas.org",
        "projecteuclid.org",
        "science.com",
        "sciencedirect.com",
        "sciencemag.org",
        "siam.org",
        "springer.com",
        "ssrn.com",
        "tandfonline.com",
        "wiley.com"
    );
    for(var i=0; i<domains.length; i++) {
        if ( dnsDomainIs(host, domains[i]) )
            return true;
    }
    return false;
}

function isDomesticDomain(url, host){
    var domains = new Array(
        "cn",
        "dp",
        "baidu.com",
        "hsiamin.com",
        "alipay.com",
        "alipay.com",
        "dianping.com",
        "dianpingoa.com",
        "qq.com",
        "taobao.com",
        "useso.com",
        "mi.com",
        "xiaomi.com"
    );
    for(var i=0; i<domains.length; i++) {
        if (dnsDomainIs(host, domains[i]) ||
            shExpMatch(host, "*." + domains[i]) )
            return true;
    }
    return false;
}

function inGFWList(url, host){
    var domains = new Array(
        "twitter.com",
        "facebook.com",
        "dropbox.com",
        "myspace.com",
        "wordpress.com",
        "greatfire.org",
        "google.com",
        "gmail.com"
    );
    for(var i=0; i<domains.length; i++) {
        if (dnsDomainIs(host, domains[i]))
            return true;
    }
    return false;
}

// function inNetSJTU(){
//     myIP = myIpAddress();
//     if (isInNet(myIP, "202.120.32.0", "255.255.255.0"))
//         return true;
//     return false;
//     return true;
// }

// function outNetSJTU(){
// }

function FindProxyForURL(url, host) {

    PROXY_SJTU = "PROXY inproxy.sjtu.edu.cn:8000; DIRECT";
    PROXY_OMNI = "PROXY jackfan.com:4000; DIRECT";
    PROXY_NONE = "DIRECT"

    if (isInNet(dnsResolve(host), "10.0.0.0", "255.0.0.0") ||
        isInNet(dnsResolve(host), "192.168.0.0", "255.255.0.0") ||
        isInNet(dnsResolve(host), "127.0.0.0", "255.255.255.0"))
        return PROXY_NONE;
        
    if (isAcademicDomain(url, host))
        return PROXY_NONE;
        
    if (isDomesticDomain(url, host))
        return PROXY_NONE;

    if (inGFWList(url, host))
        return PROXY_OMNI;
    
    return PROXY_OMNI;
}
