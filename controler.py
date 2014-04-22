# -*- encoding: utf-8 -*-
from gevent.event import AsyncResult
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


def clear_tag(input):
    if "<" in input:
        result = []
        for item in input.split("<"):
            if ">" in item:
                tag = item.split(">")[1].strip()
                if tag and "/" not in tag:
                    result.append(tag)
        return "".join(result)
    else:
        return input


def controler():
    while True:
        details = crawler.async_jump.get()
        crawler.async_jump = AsyncResult()
        parse = details["result"]["parse"]
        text = details["text"]
        result_ = copy.copy(details["result"]["result"])
        if text:
            parse(text, result_)
        crawler.async_in.set()

