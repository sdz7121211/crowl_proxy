# -*- encoding: utf-8 -*-
import sys 
reload(sys)
sys.setdefaultencoding("utf-8")
from gevent import queue
from gevent.event import AsyncResult
# from async_crawl import async_jump
# from async_crawl import async_in
# from async_crawl import async_crawl


class Observer(object):

    def __init__(self):
        self.container = queue.Queue()
        self.capacity = 0

    def inform(self, async_jump, async_in):
        while True:
            self.container.put(async_jump.get())
            self.capacity = self.capacity + 1
            async_jump = AsyncResult()
            async_in.set()

    def generator(self):
        return list(self.container.queue)

    def __call__(self, async_jump, async_in):
        self.inform(async_jump, async_in)
