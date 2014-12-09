function isAcademicDomain(url, host){
	var domains = new Array(
        "acm.org",
        "aiaa.org",
        "aps.org",
        "arxiv.org",
        "citeulike.org",
        "computer.org",
        "computer.org",
        "cshlp.org",
        "ieee.org",
        "iiisci.org",
        "iop.org",
        "jstor.org",
        "jstor.org",
        "metapress.com",
        "nature.com",
        "nih.gov",
        "nih.gov",
        "pnas.org",
        "projecteuclid.org",
        "science.com",
        "sciencedirect.com",
        "sciencemag.org",
        "sciencemag.org",
        "siam.org",
        "springer.com",
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
        "github.com",
        "qq.com",
        "taobao.com"
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
// 	myIP = myIpAddress();
// 	if (isInNet(myIP, "202.120.32.0", "255.255.255.0"))
// 		return true;
// 	return false;
// 	return true;
// }

// function outNetSJTU(){
// }

function FindProxyForURL(url, host) {

	PROXY_SJTU = "PROXY inproxy.sjtu.edu.cn:8000; DIRECT";
	PROXY_OMNI = "PROXY jackfan.com:4000; DIRECT";
	PROXY_NONE = "DIRECT"

	if (dnsResolve(host) == "127.0.0.1")
		return PROXY_NONE;

	if (inGFWList(url, host))
		return PROXY_OMNI;

    if (isAcademicDomain(url, host))
    	return PROXY_SJTU;

    if (isDomesticDomain(url, host))
    	return PROXY_NONE;

    return PROXY_OMNI;
}