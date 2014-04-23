# -*- encoding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from crawl_proxy import async_crawl
import copy
from BeautifulSoup import BeautifulSoup
import traceback
from pymongo import MongoClient
import controler

mongo_con = MongoClient("103.29.133.171", 30001)
monggo_db = mongo_con["bbscrawl1"]

crawler = async_crawl.async_crawl()


setting = {
        "website": "coolpadshequ",
        "forum_id": "1059",
        "forum_name": "手机讨论区",
        "machine_type": "kupai",
        "page_num": (1, 1000),
        "slice_url": ["http://bbs.coolpad.com/forum-", "-", ".html"]
        }


def main():
    result = {}
    result["website"] = setting["website"]
    result["forum_id"] = setting["forum_id"]
    result["forum_name"] = setting["forum_name"]
    slice_url = setting["slice_url"]
    for page in range(setting["page_num"][0], setting["page_num"][1]):
        url = "".join([slice_url[0], setting["forum_id"], slice_url[1], str(page), setting[2]])
        result_ = copy.copy(result)
        crawler.put({"url": url, "parse": parse_post_url, "result": result_})
        

profile_mapping = {
        "用户名": "username",
        "真实姓名": "real_name",
        "性别": "sex",
        "居住地": "residence",
        "手机": "phone",
        "生日": "birth",
        "QQ": "QQ",
        "你使用的酷派手机": "machine_type",
        "毕业学校": "college",
        "学历": "edu_bg",
        "职业": "profession"
        }


def parse_post_url(text, result):
    slice_url = ["http://bbs.coolpad.com/"]
    try:
        soup = BeautifulSoup(text)
        for item in soup.find("a", {"class": "s xst"}):
            result_ = copy.copy(result)
            url = "".join([slice_url[0], item["href"]])
            result_["_id"] = url
            crawler.put({"url": url, "parse": parse_post, "result": result_})
    except:
        print traceback.print_exc()


def parse_post(text, result):
    slice_url = ["http://bbs.coolpad.com/home.php?mod=space&uid=",
            "&do=profile&from=space"]
    try:
        result_copy = copy.copy(result)
        soup = BeautifulSoup(text)
        result["title"] = soup.find("span", {"id": "thread_subject"})
        author_area = soup.find("div", {"class": "authi"})
        result["author"] = author_area[0].find("a", {"class": "xi2"}).contents[0]
        result["t"] = author_area[0].find("em", {"id": True}).contents[0]
        result["content"] = controler.clear_tag(str(soup.find("td", {"class": t_f, "id": True})))
        comment_num_area = soup.find("div", {"class": "hm ptn"})
        if comment_num_area:
            tag = comment_num_area.findAll("span", {"class": "xi1"})
            result["view_num"] = tag[0].contents[0]
            result["comment_num"] = tag[1].contents[0]
        print result
        # monggo_db["post"].save(result)
        for item in author_area[1:]:
            result_ = copy.copy(result_copy)
            result_["_id"] = "".join([slice_url[0],
                item.find("a", {"class": "xi2"})["href"].split("-")[2].split(".")[0],
                slice_url[1]])
            crawler.put({"url": result_["_id"], "parse": parse_profile, "result": result_})
        result_ = copy.copy(result_copy)
        next_url = "".join(["http://bbs.coolpad.com/", soup.find("a", {"class": "nxt"})["href"]])
        crawler.put({"url": next_url, "parse": parse_comments, "result": result_})
    except:
        print traceback.print_exc()


def parse_profile(text, result):
    try:
        num = len(list(result.items()))
        soup = BeautifulSoup(text)
        info_area = soup.find("ul", {"class": "pf_l cl"})
        result_temp = {}
        if info_area:
            for item in info_area.findAll("li"):
                result_temp[item.next.strip()] = item.next.next.strip()
            for key in result_temp:
                if profile_mapping.get(key):
                    result[profile_mapping[key]] = result_temp[key]
            if len(list(result.items())) > num:
                print result
                monggo_db["profile"].save(result)
    except:
        print traceback.print_exc()


def parse_comments(text, result):
    slice_url = ["http://bbs.coolpad.com/home.php?mod=space&uid=",
            "&do=profile&from=space"]
    try:
        result_copy = copy.copy(result)
        result_copy["postid"] = result["_id"]
        soup = BeautifulSoup(text)
        comments = []
        profile_urls = []
        ts = []
        authors = []
        ids = []
        for item in soup.findAll("td", {"class": "t_f"}):
            ids.append("".join([result["website"], item["id"]]))
            comments.append(controler.clear_tag(str(item.contents)))
        author_area = soup.findAll("div", {"class": "authi"})
        for item in author_area:
            tag = item.find("a", {"class": "xi2"})
            authors.append(tag.contents[0].strip())
            ts.append(item.find("em", {"id": True}).contents[0])
            profile_urls.append(tag["href"])
        for _id, comment, profile_url, t, author in zip(ids, comments, profile_urls, ts, authors):
            store = {
                    "_id": _id,
                    "comment": comment,
                    "profile_url": profile_url,
                    "t": t,
                    "author": author}
            monggo_db["comments"].save(result_copy.update(store))
        for item in author_area:
            result_ = copy.copy(result_copy)
            result_["_id"] = "".join([slice_url[0],
                item.find("a", {"class": "xi2"})["href"].split("-")[2].split(".")[0], slice_url[1]])
            crawler.put({"url": result_["_id"], "parse": parse_profile, "result": result_})
    except:
        print traceback.print_exc()
            

        
