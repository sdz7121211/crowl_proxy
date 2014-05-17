# -*- encoding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from gevent import queue
from gevent.event import AsyncResult
from celery import Celery
from celery import group
from celery import subtask
import celeryconfig
# from async_crawl import async_jump
# from async_crawl import async_in
# from async_crawl import async_crawl
app = Celery(
        "observer",
        backend=celeryconfig.CELERY_BACKEND_RESULT,
        broker=celeryconfig.BROKER_URL
        )


class Observer(object):

    def __init__(self, obj=None):
        self.container = queue.Queue()
        self.obj = obj

    def inform(self):
        while True:
            self.container.put(obj.async_jump.get())
            obj.async_jump = AsyncResult()
            if self.container.qsize() > 10:
                group(parse.s(item) for item in self.task_args())()
            obj.async_in.set()

    def task_args(self):
        self.container.put("STOP")
        for item in iter(self.container.get, "STOP"):
            yield item
                
    def __call__(self):
        return self.inform()


@app.task
def parse(details):
    parse = details["parse"]
    text = details["text"]
    result_ = details["result"]
    if text:
        parse(text, result_)
