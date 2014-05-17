#-*- encoding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import  Queue
import thread
from bs4 import BeautifulSoup
urllis_q = Queue.Queue()
from crawl import crawl
import time 

crawler_task1 = crawl()
crawler_task2 = crawl()


def list_zhidao_url():
    url = '''http://zhidao.baidu.com/search?word=%D0%A1%C0%B1%BD%B7%CA%D6%BB%FA%D4%F5%C3%B4%D1%F9&ie=gbk&site=-1&sites=0&date=0&pn='''
    for i in range(76):
        yield url + str(i*10)


def list_zhidao_url_xiaomi():
    url = '''http://zhidao.baidu.com/search?word=%D0%A1%C3%D7%CA%D6%BB%FA%D4%F5%C3%B4%D1%F9&ie=gbk&site=-1&sites=0&date=0&pn='''
    for i in range(76):
        yield url + str(i*10)


def list_zhidao_url_coolpad():
    url = '''http://zhidao.baidu.com/search?word=%BF%E1%C5%C9%B4%F3%C9%F1%D4%F5%C3%B4%D1%F9&ie=gbk&site=-1&sites=0&date=0&pn='''
    for i in range(73):
        yield url + str(i*10)

# crawler_task1.put_list_url(list_zhidao_url())
crawler_task1.put_list_url(list_zhidao_url_coolpad())


def generator_comment_url():
    while True:
        print "crawler_task1 has page num", crawler_task1.result.qsize()
        time.sleep(1)
        html = crawler_task1.result.get()
        if html:
            try:
                soup = BeautifulSoup(html)
                for item in soup.findAll("a", {"class": "ti"}):
                    print item["href"]
                    if "zhidao" in str(item["href"]):
                        crawler_task2.put(str(item["href"]))
            except Exception, e:
                print e
from savemongo import savemongo


def getComments_zhidao():
    # f = open("./comments.txt", "a")
    while True:
        time.sleep(1)
        text = crawler_task2.result.get()
        print "crawler_task2 has page num", crawler_task2.result.qsize()
        if text:
            try:              
                lis = text.split('''class="answer-text mb-10">''')
                for item in lis[1:]:
                    comment = item.split("</pre>")[0]
                    comment = clear_comment(comment)
                    comment = comment.encode("ISO-8859-1").decode("GBK").encode("utf-8")
                    if "(" not in comment:
                        print comment
                        savemongo(website="baidu_zhidao", deal_type="comments", result=comment)
                    # if "<" not in comment:
                    # f.write(comment + "iamsplit\n")
                    pass
            except Exception, e:
                print e
                continue


def clear_comment(comment):
    temp_list = comment.split(">")
    result = []
    for item in temp_list:
        result.append(item.split("<")[0])
    comment = "".join(result)
    return "".join(comment.split('''"'''))


thread.start_new_thread(generator_comment_url, ())
thread.start_new_thread(getComments_zhidao, ())
# thread.start_new_thread(main_zhidao,())
if __name__ == "__main__":
    import time
    import gevent
    gevent.joinall([gevent.spawn(crawler_task1.start, 5), gevent.spawn(crawler_task2.start, 5)])
    time.sleep(100000)
    # crawler_task1.start(5)
    # i crawler_task2.start(5)
