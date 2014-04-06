#-*- encoding: utf-8 -*-
import gevent
from gevent import monkey
monkey.patch_all()
from util_proxy_crawl import crawl_raw
from util_proxy_crawl import crawl_effective
from util_proxy_crawl import available_proxy
from gevent import queue
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class crawl:
   
    def __init__(self):
        self.available_proxy = available_proxy
        self.url_qu = queue.JoinableQueue()
        self.stop = True

    def put(self, url):
        self.url_qu.put(url)
    
    def put_list_url(self, urls): 
        for url in urls:
            self.put(url)

    def run(self, task):
        print "task num", task
        while not self.url_qu.empty():
            url = self.url_qu.get()
            try:
                self.crawl_raw(url)
            except Exception, e:
                print e
            finally:
                self.url_qu.task_done()


    def crawl_raw(self, url):
        return crawl_raw(url)

    def crawl_effective(self, url):
        return crawl_effective(url)

    def start(self):
        #self.stop = False
        self.crawls = [gevent.spawn(self.run, i) for i in range(5)]
        self.url_qu.join()
        #while not self.stop:

            

    def stop_crawl(self):
        self.stop = True


if __name__ == "__main__":
    tester = crawl()
    url = ["http://www.cnproxy.com/proxy1.html"]
    tester.put_list_url(url*5)
    tester.start()
