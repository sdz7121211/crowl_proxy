#-*- encoding: utf-8 -*-
from crawl import crawl
import gevent
from gevent.event import AsyncResult
from gevent.pool import Group
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
global async_jump
async_jump = AsyncResult()

class async_crawl(crawl):
    global async_jump

    def __init__(self):
        crawl.__init__(self)

    def put(self, url):
        super(async_crawl, self).put(url)
        self.job_size = self.url_qu.qsize()

    def put_list_url(self, urls):
        super(async_crawl, self).put_list_url(urls)
        self.job_size = self.url_qu.qsize()
    
    def setObserver(self, observer):
        self.observer = observer
        
    def run(self, i):
        print "task ", i
        while not self.url_qu.empty():
            url = self.url_qu.get()
            try:
                text = self.crawl_raw(url)
                self.result.put(text)
                if self.result.qsize() > self.job_size/3:
                    async_jump.set(self.result)
                #if self.result.qsize() 
                #gevent.sleep(0)
            except Exception, e:
                print e
            finally:
                self.url_qu.task_done()

    def start(self, num):
       #self.work_group = Group()
       #[gevent.spawn(self.run, i) for i in range(num)]
       #gevent.spawn(self.observer)
       #self.url_qu.join()
        gevent.joinall([gevent.spawn(self.run, i) for i in range(num), gevent.spawn(self.observer)])
#----------TEST CODE-----------
def observer_test():
    global async_jump
    print "wait before"
    print "-----------------", async_jump.get()
    print "wait after"

if __name__ == "__main__":
    url = ["http://www.cnproxy.com/proxy1.html"]
    async = async_crawl()
    async.setObserver(observer_test)
    async.put_list_url(url*5)
    async.start(5)
