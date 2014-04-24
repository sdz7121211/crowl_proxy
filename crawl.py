# -*- encoding: utf-8 -*-
import gevent
from gevent import monkey
# from gevent.event import AsyscResult
from gevent.pool import Group
monkey.patch_all()
from util_proxy_crawl import crawl_raw
from util_proxy_crawl import crawl_effective
from util_proxy_crawl import available_proxy
from proxy_crawl import header
from gevent.queue import PriorityQueue
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class crawl(object):

    def __init__(self):
        self.available_proxy = available_proxy
        self.url_qu = PriorityQueue()
        self.result = PriorityQueue()

    def put(self, url, priority=1):
        self.url_qu.put(url, priority)

    def put_list_url(self, urls):
        for url in urls:
            self.put(url)

    def run(self, task):
        print "task ", task
        while True:
            url = self.url_qu.get(timeout=100)
            try:
                text = self.crawl_raw(url)
                self.result.put(text)
                gevent.sleep(0)
            except Exception, e:
                print e
            finally:
                self.url_qu.task_done()

    def setHeaders(self, **kws):
        for key in kws:
            header[key] = kws[key]

    def crawl_raw(self, url):
        return crawl_raw(url)

    def crawl_effective(self, url):
        return crawl_effective(url)

    def start(self, num):
        self.g = Group()
        [self.g.add(gevent.spawn(self.run, i)) for i in range(num)]
        self.url_qu.join()



if __name__ == "__main__":
    tester = crawl()
    url = ["http://www.cnproxy.com/proxy1.html"]
    tester.setHeaders(cookie="testcookie")
    tester.put_list_url(url*5)
    tester.start(5)
    print tester.result.qsize()
