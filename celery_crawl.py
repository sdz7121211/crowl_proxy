# -*- encoding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from Observer import Observer
from async_crawl import async_crawl


class celery_crawl(async_crawl):

    def __init__(self):
        super(celery_crawl, self).__init__(self)
        self.observer = Observer(self)
