#-*- encoding: utf-8 -*-
import requests
from requests import Request, Session
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip,deflate,sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            # "Host":"www.oschina.net"
            "Referer": "https://www.google.com.hk/",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36"
        }


def crawl_GET(url, proxies=None, params=None):
    s = Session()
    req = Request(
                    "GET", url,
                    params=params,
                    headers=header)
    prep = s.prepare_request(req)
    if not proxies:
        proxies = get_proxies()
    resp = s.send(
                    prep,
                    proxies=proxies,
                    timeout=5)                 
    if resp.status_code == 200:
        return resp.text
    else:
        return None


global continer_proxy


def load_proxies():
    global continer_proxy
    f = open("out.txt")
    continer_proxy = []
    for item in f.readlines():
        item = item.strip()
        continer_proxy.append({"http": "".join(["http://", item])})


def get_proxies():
    global continer_proxy
    import random
    return random.choice(continer_proxy)

load_proxies()

def getHtml(url, proxies=None, params=None):
    while True:
        try:
            result = crawl_GET(url, proxies, params)
            proxies = None
            if result:
                return result
            else:
                continue
        except Exception, e:
            print e
            continue



def test():
    url = "http://zhidao.baidu.com/question/557035252.html"
    print getHtml(url)

if __name__ == "__main__":
    for loop in range(100):
    #    print get_proxies()
        #try:
        print loop, test()
        #except Exception, e:
            #print e
