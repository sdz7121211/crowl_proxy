# -*- encoding: utf-8 -*-
from crawl import crawl
import gevent
from gevent.event import AsyncResult
from gevent.pool import Group
import sys
import copy
reload(sys)
sys.setdefaultencoding("utf-8")


class async_crawl(crawl):

    def __init__(self):
        crawl.__init__(self)
        self.async_jump = AsyncResult()
        self.async_in = AsyncResult()
        self.finished = AsyncResult()
        self.observer = self.controler

    def put(self, url, priority=1):
        super(async_crawl, self).put(url, priority)
        self.job_size = self.url_qu.qsize()

    def put_list_url(self, urls):
        super(async_crawl, self).put_list_url(urls)
        self.job_size = self.url_qu.qsize()

    def setObserver(self, observer):
        self.observer = observer

    def controler(self):
        try:
            while True:
                details = self.async_jump.get(timeout=20)
                self.async_jump = AsyncResult()
                parse = details["parse"]
                text = details["text"]
                result_ = details["result"]
                if text:
                    parse(text, result_)
                self.async_in.set()
        except Exception, e:
            print "controler", e
            return

    def run(self, i):
        task_num = self.job_size
        while True:
            print "task ", i
            try:
                details = self.url_qu.get(timeout=20)
                result = details["result"]
                url = details["url"]
                print "crawl url", url
            except Exception, e:
                print "Exception crawl run: ", e
                task_num = task_num - 1
                break
            try:
                text = self.crawl_raw(url)
                self.async_jump.set({"url": url, "text": text, "result": result, "parse": details["parse"]})
                self.async_in.get(timeout=20)
                self.async_in = AsyncResult()
            except Exception, e:
                print e
            # finally:
            #    self.url_qu.task_done()
        print "task", i, "finished. Has task_num:", task_num

    def start(self, num):
        gevent.joinall([gevent.spawn(self.run, i) for i in range(num)]+[gevent.spawn(self.observer)])


# ----------TEST CODE-----------
def observer_test(async_jump, async_in):
    # global async_jump, async_in
    while True:
        print "wait before"
        async_jump.get()
        async_jump = AsyncResult()
        print "-----------------",
        print "wait after"
        async_in.set()

if __name__ == "__main__":
    url = ["http://www.cnproxy.com/proxy1.html"]
    # async = async_crawl()
    # async.setObserver(observer_test)
    # async.put_list_url(url*5)
    # async.start(5)
    from observer import Observer
    tester = Observer()
    async = async_crawl()
    async.setObserver(tester.inform)
    async.put_list_url(url*5)
    async.start(5)
