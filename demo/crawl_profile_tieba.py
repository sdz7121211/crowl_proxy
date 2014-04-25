# -*- encoding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from crawl_proxy import async_crawl
from pymongo import MongoClient
from BeautifulSoup import BeautifulSoup
import traceback

cookie = '''fuwu_center_bubble=1; BAIDUID=425D8E21E2E712F5781F974CDE28EE89:FG=1; TIEBA_USERTYPE=5bb88ae83bd9e05cd18f9a2c; bdshare_firstime=1396541193479; head_skin_guide=1; H_PS_PSSID=6173_6043_1457_5224_6024_4759_6018_6257_5857_5824; BDUSS=hKTElkOEt5eHlGOWNtbmtycFZrczJCTmFhZDlFZURCNVB1eERZYWZMWnRUb0ZUQVFBQUFBJCQAAAAAAAAAAAEAAAA2REwsc2R6NzEyMTIxMQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAG3BWVNtwVlTZn; TIEBAUID=d5dbceec3fbe6e9d1eccd586'''

host = "tieba.baidu.com"

mongo_con = MongoClient("103.29.133.171", 30001)
mongo_db = mongo_con["bbscrawl1"]
mongo_save = mongo_db["attention"]
crawler = async_crawl.async_crawl()
crawler.setHeaders(Cookie=cookie)
crawler.setHeaders(Host=host)

find_ = {
        "forum_id": {"$in": ["xiaolajiao", "beidouxiaolajiao", "beidouxingxialajiao", "xiaolajiaodianxinba"]}}

global count
count = 0


def start():
    global count
    for item in mongo_db["comments"].find(find_):
        count = count + 1
        result = {}
        result["_id"] = item["_id"]
        result["name"] = item.get("name")
        result["website"] = item.get("website")
        result["forum_id"] = item.get("forum_id")
        result["forum_name"] = item.get("forum_name")
        result["tieba_profile_url"] = item.get("tieba_profile_url")
        crawler.put({"url": result["tieba_profile_url"], "parse": parse_attention, "result": result})
    crawler.start(10)
    print "-------------------", count, "---------------------"


def parse_attention(text, result):
    try:
        soup = BeautifulSoup(text)
        attention_area = soup.find("div", {"id": "forum_group_wrap"})
        attention = []
        if attention_area:
            for item in attention_area.findAll("a", {"class": "u-f-item unsign"}):
                attention.append(item.find("span").contents[0])
            result["attention"] = attention
        if result.get("attention"):
            print result
            mongo_save.save(result)
    except:
        print traceback.print_exc()

if __name__ == "__main__":
    start()
