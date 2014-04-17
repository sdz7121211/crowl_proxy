#-*- encoding: utf-8 -*-
import gevent
from proxy_crawl import crawl_GET
from proxy_crawl import load_proxies
from proxy_crawl import get_proxies
from proxy_crawl import continer_proxy
from proxy_crawl import getHtml
from gevent.queue import Queue
import random
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


global available_proxy
available_proxy = []


def crawl_raw(url):
    global available_proxy
    while 1:
        if len(available_proxy) < 60:
            proxy = get_proxies()
            try:
                print "i am crawl_raw"
                text = crawl_GET(url, proxy)
                print proxy
                if proxy not in available_proxy:
                    available_proxy.append(proxy)
                    print available_proxy
                return text
            except Exception, e:
                print "crawl_raw-Exception", e
                continue
        else:
            return crawl_effective(url)
            #gevent.sleep(0)


def crawl_effective(url):
    global available_proxy
    while 1:
        #print "len(available_proxy)", len(available_proxy)
        if len(available_proxy) >= 50:
            proxy = random.choice(available_proxy)
            print "i am crawl_effective"
            try:
                text = crawl_GET(url, proxy)
                return text
            except Exception, e:
                print e
                del available_proxy[available_proxy.index(proxy)] 
        else:
            return crawl_raw(url)
            #gevent.sleep(0)


#-----TEST CODE---------------
qu = gevent.queue.Queue()

def product_url():
    for i in range(100):
        print "product"
        qu.put("http://www.cnproxy.com/proxy1.html")
    print qu.qsize()

def crawl_raw_test():
    count = 0
    gevent.sleep(2)
    print "wake up crawl_raw_test"
    while not qu.empty():
        url = qu.get()
        crawl_raw(url)
        count = count + 1
        print "crawl_raw_test run num",count
        gevent.sleep(0)


def crawl_effective_test():
    count = 0
    gevent.sleep(2)
    print "crawl_effective_test wake up"
    while not qu.empty():
        url = qu.get()
        crawl_effective(url)
        count = count + 1
        print "crawl_effective_test run num",count
        gevent.sleep(0)

if __name__ == "__main__":
    gevent.joinall([gevent.spawn(product_url), gevent.spawn(crawl_raw_test), gevent.spawn(crawl_effective_test)])
#    gevent.spawn(product_url)
#    gevent.spawn(crawl_raw_test)
#    gevent.spawn(crawl_effective_test)
#    import time
#    print "--------------------"
#    time.sleep(10000)
