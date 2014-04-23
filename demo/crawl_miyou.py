# -*- encoding: utf-8 -*-
from gevent.event import AsyncResult
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from crawl_proxy import async_crawl
import copy
from pymongo import MongoClient
from BeautifulSoup import BeautifulSoup
import traceback
from schema_mappings import profile_mapping_miui 
mongo_con = MongoClient("103.29.133.171", 30001)
mongo_db = mongo_con["bbscrawl1"]

crawler = async_crawl.async_crawl()

setting = {
        "website": "miui",
        "slice_url": ['''http://www.miui.com/forum-''', '''-''', '''.html'''],
        "forum_id": [192],  #, 370, 23, 440],
        "page_num": [(1, 1000)],  #, 854, 1195, 35],
        "tag": ["xiaomi2"]  #, "xiaomi3", "hongmi1", "hongminote"]
        }

setting_huafen = {
        "website": "huafen",
        "slice_url": ['''http://cn.ui.vmall.com/forum.php?mod=forumdisplay&fid=''', '''&page='''],
        "forum_id": ["308"],
        "page_num": [(1900, 2000)],
        "tag": ["rongyao3c"]
        }

def tasks(kws):
    forum_ids = kws["forum_id"]
    page_nums = kws["page_num"]
    tags = kws["tag"]
    del kws["forum_id"]
    del kws["page_num"]
    del kws["tag"]
    task = []
    for forum_id, page_num, tag in zip(forum_ids, page_nums, tags):
        temp = kws.copy()
        temp["forum_id"] = forum_id
        temp["page_num"] = page_num
        temp["tag"] = tag
        print temp
        yield temp
        # task.append(temp)  


def parse_profile_miui(text, result):
    try:
        result_ = {}
        soup = BeautifulSoup(text)
        tbody = soup.find("tbody")
        if tbody:
            try:
                for key, value in zip(tbody.contents[0], tbody.contents[1]):
                    result_[key.string] = clear_tag(value.contents[0])
            except:
                print traceback.print_exc()
        for key in soup.findAll("span", {"class": "th"}):
            try:
                if key.nextSibling.name == u"span":
                    result_[key.string] = key.nextSibling.contents[0]
            except:
                print traceback.print_exc()
        for key, value in result_.items():
            if profile_mapping_miui.get(key):
                result[profile_mapping_miui[key]] = value
        mongo_db["profile"].save(result)
    except:
        print traceback.print_exc()


def parse_post_url(text, result):
    try:
        soup = BeautifulSoup(text)
        for item in soup.findAll("a", {"class": "s xst"}):
            url = "".join(["http://www.miui.com/", item["href"]])
            result_ = copy.copy(result)
            result_["_id"] = url
            crawler.put({"url": url, "parse": parse_post, "result": result_})
    except:
        print traceback.print_exc()


def parse_post(text, result):
    try:
        soup = BeautifulSoup(text)
        title = soup.find("a", {"id": "thread_subject"}).string
        content = clear_tag(str(soup.find("td", {"class": "t_f"})))
        view_num = soup.find("span", {"class": "z as_views"}).contents[0]
        comment_num = soup.find("span", {"class": "z as_replies"}).contents[0]
        author = soup.find("div", {"class": "authi z"}).contents[0].contents[0]
        uid = soup.find("div", {"class": "authi z"}).contents[0]["href"]
        result["title"] = title
        result["content"] = content
        result["view_num"] = view_num
        result["comment_num"] = comment_num
        result["author"] = author
        result["uid"] = uid
        mongo_db["post"].save(result)
    except:
        print traceback.print_exc()


def parse_post_url_huafen(text, result):
    try:
        soup = BeautifulSoup(text)
        for item in soup.findAll("a", {"class": "s xst"}):
            url = "".join(["http://cn.ui.vmall.com/", item["href"]])
            result_ = copy.copy(result)
            result_["_id"] = url
            print url
            crawler.put({"url": url, "parse": parse_post_huafen, "result": result_})
    except:
        print traceback.print_exc()


def parse_post_huafen(text, result):
    try:
        soup = BeautifulSoup(text)
        title = soup.find("span", {"id": "thread_subject"}).string
        content = clear_tag(str(soup.find("td", {"class": "t_f"})))
        view_num = soup.find("span", {"class": "hbw-ico hbwi-view14"}).contents[0]
        comment_num = soup.find("a", {"class": "hbw-ico hbwi-reply14"}).contents[0]
        area = BeautifulSoup("".join(map(str, soup.find("div", {"class": "authi"}).contents)))
        author = area.find("a", {"class": "xi2"}).contents[0].strip()
        t = area.find("em")
        if t:
            t = t.contents[0]
        elif area.find("span"):
            t = area.find("span")["title"]
        uid = soup.find("div", {"class": "authi"}).contents[1]["href"]
        result["title"] = title
        result["content"] = content
        result["view_num"] = view_num
        result["comment_num"] = comment_num
        result["author"] = author
        result["uid"] = uid.split("=")[-1]
        mongo_db["post"].save(result)
    except:
        print traceback.print_exc()


def parse_comment_huafen(text, result):
    try:
        soup = BeautifulSoup(text)
        next_url = soup.find("a", {"class": "nxt"})
        if next_url:
            next_url = "".join(["http://cn.club.vmall.com/", next_url["href"]])
            result_ = copy.copy(result)
            result_["url"] = next_url
            crawler.put({"url": next_url, "result": result_, "parse": parse_comment_huafen})
        comments_area = soup.findAll("td", {"class": "t_f"})[1:]
        comments = []
        id = []
        for item in comments_area:
            comments.append(clear_tag(item.contents[0]))
            id.append(item["id"])
        tieba_profile_url = []
        name = []
        t = []
        postid = result["_id"]
        author_area = soup.findAll("div", {"class": "authi"})[1:]
        if author_area:
            for item in author_area:
                soup_ = BeautifulSoup(str(item))
                tag1 = soup_.find("a", {"class": "xi2"})
                tieba_profile_url.append("".join(["http://cn.club.vmall.com/", tag1["href"]]))
                name.append(tag1.string)
                t.append(soup_.find("em", {"id": True}).contents[0])
        store = {}
        store["website"] = result["website"]
        store["forum_id"] = result.get("forum_id")
        if result.get("url"):
            store["url"] = result["url"]
        else:
            store["url"] = result["_id"]
        for id_, comment, profile_url, na, t_ in zip(id, comments, tieba_profile_url, name, t):
            # print id_, comment, profile_url, na, t_
            store.update({"_id": id_, "postid": postid, "comment": comment, "tieba_profile_url": profile_url, "name": na, "t": t_}) 
            print store
            mongo_db["comments"].save(store)
    except:
        print traceback.print_exc()


def parse_comment_miui(text, result):
    try:
        soup = BeautifulSoup(text)
        next = soup.find("a", {"class": "nxt"})
        if next:
            if result.get("url"):
                page_num = result.get("url").split("-")[2]
                if page_num > "100":
                    pass
                else:
                    next_url = "".join(["http://www.miui.com/", next["href"]])
                    result["url"] = next_url
                    crawler.put({"url": next_url, "parse": parse_comment_miui, "result": result})
        store = {}
        store["website"] = result["website"]
        store["forum_id"] = result["forum_id"]
        store["url"] = result["_id"]
        comments = []
        t = []
        id = []
        tieba_profile_url = []
        name = []
        for item in soup.findAll("td", {"class": "t_f"})[1:]:
            id.append("".join([store["website"], item["id"]]))
            comments.append(clear_tag(item.contents[0]))
        for item in soup.findAll("div", {"class": "authi z"})[1:]:
            tieba_profile_url.append("".join(["http://www.miui.com/", item.a["href"]]))
            name.append(item.a.contents[0])
        for item1 in soup.findAll("div", {"class": "authi"})[1:]:
            if item1.find("span", {"title": True}):
                t.append(item1.find("span", {"title": True})["title"])
            elif item1.find("em"):
                t.append(item1.find("em").contents[0])
        mongo_collection = mongo_db["comments"]
        for comment, t_, profile_url, na, id_ in zip(comments, t, tieba_profile_url, name, id):
            store.update({"comments": comment, "t": t_, "tieba_profile_url":profile_url, "name": na, "_id": id_})
            print store
            mongo_collection.save(store)

    except:
        print traceback.print_exc()


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


def crawl_post_miui():
    for task in tasks(setting):
        result = {}
        result["website"] = task["website"]
        result["forum_id"] = task["tag"]
        forum_id = task["forum_id"]
        page = task["page_num"]
        slice_url = task["slice_url"]
        for page in range(page[0], page[1]+1):
            url = "".join([slice_url[0], str(forum_id), slice_url[1], str(page), slice_url[2]])
            crawler.put({"url": url, "result": result, "parse": parse_post_url})
    crawler.setObserver(controler)
    crawler.start(10)


def crawl_post_huafen():
    for task in tasks(setting_huafen):
        result = {}
        result["website"] = task["website"]
        result["forum_id"] = task["tag"]
        forum_id = task["forum_id"]
        page = task["page_num"]
        slice_url = task["slice_url"]
        for page in range(page[0], page[1]+1):
            url = "".join([slice_url[0], str(forum_id), slice_url[1], str(page)])
            print url
            crawler.put({"url": url, "result": result, "parse": parse_post_url_huafen})
    crawler.setObserver(controler)
    crawler.start(10)


def crawl_comment_huafen():
    mongo_collection = mongo_db["post"]
    for item in mongo_collection.find({"website": "huafen"}):
        url = item["_id"]
        print "-------", url
        crawler.put({"url": url, "result": item, "parse": parse_comment_huafen})
    crawler.setObserver(controler)
    crawler.start(10)


def crawl_profile_miui():
    def get_url(part_url):
        slice_url = ["http://www.miui.com/home.php?mod=space&uid=", "&do=profile"]
        uid = part_url[part_url.rfind("-")+1: part_url.rfind(".")]
        return "".join([slice_url[0], uid, slice_url[1]]), uid
    result = {}
    for item in mongo_db["post"].find({"website": "miui", "forum_id": {"$in": ["xiaomi2", "xiaomi3", "hongmi1", "hongminote"]}}):
        print item["uid"]
        result["website"] = item["website"]
        result["name"] = item["author"]
        result["forum_id"] = item["forum_id"]
        url, uid = get_url(item["uid"])
        result["_id"] = "".join([result["website"], "-", uid])
        result_ = copy.copy(result)
        crawler.put({"url": url, "result": result_, "parse": parse_profile_miui})
    crawler.setObserver(controler)
    crawler.start(10)


def crawl_comment_miui():
    mongo_collection = mongo_db["post"]
    for item in mongo_collection.find({"website": "miui"}):
        url = item["_id"]
        crawler.put({"url": url, "parse": parse_comment_miui, "result": item})
    crawler.setObserver(controler)
    crawler.start(10)

if __name__ == "__main__":
    crawl_comment_miui()
