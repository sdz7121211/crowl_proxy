#-*- encoding: utf-8 -*-
from gevent.event import AsyncResult
import copy
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
from BeautifulSoup import BeautifulSoup
from crawl_proxy import controler 
from crawl_proxy import async_crawl
from pymongo import MongoClient
import traceback

Cookie = '''bdshare_firstime=1398219000124; focs_2132_saltkey=4LJc84tT; focs_2132_lastvisit=1398216795; Hm_lvt_2a6c125b2167aee59ec48d03afe04305=1398220402,1398221031; Hm_lpvt_2a6c125b2167aee59ec48d03afe04305=1398221067; focs_2132_seccodeS1Xyy5P0=eb5f6qzl6r%2FwsJfsnhQ2NRVUl2yaIY4MgLDu%2BSCipbslDwLKn5esi7Yyd0lZ%2B%2BtlDDTbIz90NuwvFIppb9s; focs_2132_ulastactivity=f28020MuFFSIi43JGKabbVJe4nWlQodV7Zmuewc6d60Zxllh%2FfcD; focs_2132_auth=7edf3E5G8JoAMipLpaQv9RnACwnwVa2tTqbBulQxzoyX3z0YN2qXKJ2%2F6%2FQvfkL8MMCYY6ZgJRYtmyomTdTPDGTEhlU; focs_2132_myrepeat_rr=R0; focs_2132_visitedfid=64D41; focs_2132_viewid=tid_145563; focs_2132_home_diymode=1; focs_2132_sid=z7Q3jJ; focs_2132_lastact=1398232782%09home.php%09misc; focs_2132_connect_is_bind=0; focs_2132_sendmail=1; SERVERID=e290eaec2b5794133d4489bf78fdcf38|1398232782|1398232781; pgv_pvi=5145345187; pgv_info=ssi=s8234151013; focs_2132_noticeTitle=1; __utma=59093810.1611070933.1398218926.1398223083.1398232783.3; __utmb=59093810.1.10.1398232783; __utmc=59093810; __utmz=59093810.1398218927.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _ga=GA1.2.1611070933.1398218926; tjpctrl=1398234583162'''

Host = "bbs.nubia.cn"

Referer = "http://bbs.nubia.cn/forum.php?mod=forumdisplay"
global count
count = 0

crawler = async_crawl.async_crawl()
crawler.setHeaders(Cookie=Cookie, Host=Host, Referer=Referer)

mongo_con = MongoClient("103.29.133.171", 30001)
mongo_db = mongo_con["bbscrawl1"]

setting = {
        "website": "nubiyashequ",
        "slice_url": ["http://bbs.nubia.cn/forum.php?mod=forumdisplay&page="],
        "page_num": (1, 100),
        "forum_id": "nubiya"
        }


def main():
    result = {}
    result["website"] = setting["website"]
    result["forum_id"] = setting["forum_id"]
    for page in range(setting["page_num"][0], setting["page_num"][1]):
        url = "".join([setting["slice_url"][0], str(page)])
        result_ = copy.copy(result)
        crawler.put({"url": url, "parse": parse_post_url, "result": result_})
    crawler.start(15)


def parse_post_url(text, result):
    try:
        soup = BeautifulSoup(text)
        for item in soup.findAll("a", {"class": "xst"}):
            url = "".join(["http://bbs.nubia.cn/", item["href"]])
            result_ = copy.copy(result)
            result_["_id"] = url
            crawler.put({"url": url, "result": result_, "parse": parse_post})
    except:
        print traceback.print_exc()


def parse_post(text, result):
    global count
    count = count + 1
    print "------------------------------------", count, "------------------------------------------"
    slice_url = ["http://bbs.nubia.cn/"]
    try:
        soup = BeautifulSoup(text)
        title = soup.find("span", {"class": "ts"}).find("a", {"id": "thread_subject"}).contents[0]
        author_area = soup.findAll("div", {"class": "authi"})
        author = author_area[0].find("a", {"class": "xw1"}).contents[0]
        tieba_profile_url = author_area[0].find("a", {"class": "xw1"})["href"]
        comment_area = soup.find("div", {"class": "hm"})
        if comment_area.find("span", {"title": True}):
            view_num = comment_area.find("span", {"title": True})["title"].strip()
        else:
            view_num = comment_area.findAll("span", {"class": "xi1"})[1].contents[0].strip()
        comment_num = comment_area.findAll("span", {"class": "xi1"})[3].contents[0].strip()
        t = soup.find("div", {"class": "msg"}).find("span", {"title": True})
        if t:
            t = t["title"]
        else:
            t = soup.find("div", {"class": "msg"}).find("em", {"id": True}).contents[0].strip()
        content = controler.clear_tag(str(soup.find("td", {"class": "t_f"})))
        next_url = soup.find("a", {"class": "nxt"})
        if next_url:
            next_url = next_url["href"]
            next_url = "".join([slice_url[0], next_url])
            result_ = result.copy()
            result_["url"] = next_url
            crawler.put({"url": next_url, "parse": parse_comments, "result": result_})
        result.update({
            "title": title,
            "author": author,
            "tieba_profile_url": tieba_profile_url,
            "view_num": view_num,
            "comment_num": comment_num,
            "t": t,
            "content": content})
        mongo_db["post"].save(result)
    except:
        print traceback.print_exc()


profile_mapping = {
        u"性别": "sex",
        u"出生地": "borth_address",
        u"毕业学校": "college",
        u"学历": "edu_bg",
        u"公司": "company",
        u"职业": "profession",
        u"职位": "post"
        }


global count_profile
count_profile = 0
def parse_profile(text, result):
    global count_profile
    count_profile = count_profile + 1
    print "----------------------------profile:", count_profile, "-----------------------------------"
    try:
        soup = BeautifulSoup(text)
        area = soup.find("ul", {"class": "pf_l cl"})
        result_ = {}
        for item in area.findAll("li"):
            result_[item.find("em").contents[0].strip()] = item.find("em").next.next.strip()
        store = {}
        store["website"] = result["website"]
        store["forum_id"] = result["forum_id"]
        store["_id"] = result["url"]
        for key in result_:
            print key
            if profile_mapping.get(key.strip()):
                store[profile_mapping.get(key.strip())] = result_[key]
        if len(list(store.items())) > 3:
            print store
            mongo_db["profile"].save(store)
    except:
        print traceback.print_exc()


global count_comment
count_comment = 0
def parse_comments(text, result):
    global count_comment
    count_comment = count_comment + 1
    print "---------------------------comment:", count_comment, "-----------------------------------------"
    slice_url = ["http://bbs.nubia.cn/"]
    url_slice = ["http://bbs.nubia.cn/home.php?mod=space&uid=", "&do=profile"]
    try:
        soup = BeautifulSoup(text)
        area_list = soup.findAll("td", {"class": "plc post_content"})[1:]
        comments = []
        names = []
        tieba_profile_url = []
        ts = []
        _ids = []
        url = result["url"]
        website = result["website"]
        forum_id = result["forum_id"]
        for item in area_list:
            tag_t = item.find("em", {"id": True})
            _ids.append("".join([website, tag_t["id"]]))
            if tag_t.find("span", {"title": True}):
                ts.append(tag_t.find("span", {"title": True})["title"])
            else:
                ts.append(tag_t.contents[0].strip())
            tag_comment = item.find("td", {"class": "t_f"})
            comments.append(controler.clear_tag(str(tag_comment)).strip())
        for item in soup.findAll("a", {"class": "xw1"})[1:]:
            tieba_profile_url.append("".join(["http://bbs.nubia.cn/", item["href"]]))
            names.append(item.contents[0])
            print item["href"]
            uid = item["href"].split("-")[2].split(".")[0]
            url_ = "".join([url_slice[0], uid, url_slice[1]])
            result["url"] = url_
            result_ = result.copy()
            crawler.put({"url": url_, "parse": parse_profile, "result": result_})
        for _id, comment, name, profile_url, t in zip(_ids, comments, names, tieba_profile_url, ts):
            result.update({
                "_id": _id,
                "comment": comment,
                "name": name,
                "tieba_profile_url": profile_url,
                "t": t,
                "url": url,
                "website": website})
            mongo_db["comments"].save(result)
            next_url = soup.find("a", {"class": "nxt"})
            if next_url:
                next_url = next_url["href"]
                next_url = "".join([slice_url[0], next_url])
                result_ = result.copy()
                result_["url"] = next_url
                crawler.put({"url": next_url, "parse": parse_comments, "result": result_})
    except:
        print traceback.print_exc()


if __name__ == "__main__":
    main()
