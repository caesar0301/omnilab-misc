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
        "123rf.com",
        "4shared.com",
        "adultfriendfinder.com",
        "amazonaws.com",
        "android.com",
        "anysex.com",
        "appledaily.com.tw",
        "archive.org",
        "asos.com",
        "*bbc.co*",
        "backpage.com",
        "beeg.com",
        "bestadbid.com",
        "bet365.com",
        "bitshare.com",
        "blogger.com",
        "bloglovin.com",
        "blogspot.*",
        "bloomberg.com",
        "bravotube.net",
        "cam4.com",
        "change.org",
        "citibank.com",
        "cj.com",
        "ck101.com",
        "comcast.net",
        "dailymotion.com",
        "deviantart.com",
        "doubleclick.com",
        "dropbox.com",
        "drtuber.com",
        "duckduckgo.com",
        "ebay.de",
        "ehow.com",
        "elpais.com",
        "evernote.com",
        "expedia.com",
        "eyny.com",
        "facebook.com",
        "fc2.com",
        "feedburner.com",
        "flickr.com",
        "freelancer.com",
        "github.com",
        "globo.com",
        "gmail.com",
        "goo.gl",
        "*google.*",
        "googleadservices.com",
        "googleapis.com",
        "greatfire.org",
        "gsmarena.com",
        "gstatic.com",
        "gutefrage.net",
        "habrahabr.ru",
        "hardsextube.com",
        "heise.de",
        "hidemyass.com",
        "hootsuite.com",
        "huffingtonpost.com",
        "ifilez.org",
        "imdb.com",
        "instagram.com",
        "intel.com",
        "istockphoto.com",
        "lemonde.fr",
        "liveleak.com",
        "logmein.com",
        "mackolik.com",
        "macys.com",
        "mobile01.com",
        "motherless.com",
        "netflix.com",
        "nuvid.com",
        "nytimes.com",
        "odesk.com",
        "ouedkniss.com",
        "*orange*.com",
        "pastebin.com",
        "pchome.com.tw",
        "pixnet.net",
        "pornhub.com",
        "pornhublive.com",
        "putlocker.com",
        "reddit.com",
        "redtube.com",
        "reuters.com",
        "scribd.com",
        "sex.com",
        "sfgate.com",
        "sfr.fr",
        "shutterstock.com",
        "slideshare.net",
        "soundcloud.com",
        "spankwire.com",
        "speedtest.net",
        "squidoo.com",
        "steampowered.com",
        "subito.it",
        "swagbucks.com",
        "t.co",
        "terra.com.br",
        "theblaze.com",
        "theguardian.com",
        "thepiratebay.se",
        "trello.com",
        "tube8.com",
        "tumblr.com",
        "turbobit.net",
        "twitch.tv",
        "twitter.com",
        "udn.com",
        "viadeo.com",
        "vimeo.com",
        "webs.com",
        "wordpress.com",
        "wsj.com",
        "xhamster.com",
        "xing.com",
        "xtube.com",
        "xvideos.com",
        "yahoo.com",
        "youporn.com",
        "yourlust.com",
        "youtube.com"
    );
    for(var i=0; i<domains.length; i++) {
        if (dnsDomainIs(host, domains[i]) || shExpMatch(host, domains[i]))
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
        
    if (isDomesticDomain(host, url))
        return PROXY_NONE;
        
    if (isAcademicDomain(url, host))
        return PROXY_SJTU;

    if (inGFWList(url, host))
        return PROXY_OMNI;
    
    return PROXY_SJTU;
}
