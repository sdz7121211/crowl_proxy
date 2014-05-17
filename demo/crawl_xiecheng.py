# -*- encoding: utf-8 -*-
import sys
import gevent
reload(sys)
sys.setdefaultencoding("utf-8")
from crawl_proxy import async_crawl
import copy
from BeautifulSoup import BeautifulSoup
import csv
import traceback
import time
from gevent.event import AsyncResult
import datetime
from datetime import date, timedelta

Cookie = """CookieSession=SmartLinkLanguage=zh&SmartLinkHost=&SmartLinkQuary=&SmartLinkKeyWord=&SmartLinkCode=U155952; Union=OUID=baidu81%7Cindex%7C%7C%7C&AllianceID=4897&SID=155952; _abtest_=796d50fd-b6ab-4e56-a1ed-84cd706d9e1c; _bfp=_bfp1984750890; _bfa=1.1398921467088.2e66br.1.1398921467088.1398921467088.1.12; _bfs=1.12; traceExt=campaign=CHNbaidu81&adid=index; __utma=1.869506203.1398921467.1398921467.1398921467.1; __utmb=1.11.10.1398921467; __utmc=1; __utmz=1.1398921467.1.1.utmcsr=baidu|utmccn=baidu81|utmcmd=cpc|utmctr=ctrip; _bfi=p1%3D102002%26p2%3D100003%26v1%3D12%26v2%3D11; zdata=zdata=/EzoLdWMgtWHZvM7bhVmpZm+FyQ=; bid=bid=F; AX_HOTELS-20480-hotels_domestic=BBACAIAKFAAA; __zpspc=9.1.1398921472.1398923878.9%234%7C%7C%7C%7C%7C; zdatactrip=zdatactrip=eff9814d8763f490; HotelCityID=1split%E5%8C%97%E4%BA%ACsplitBeijingsplit2014-05-01split2014-05-02split0; HotelDomesticVisitedHotels1=804318=0,,4.2,1331,/hotel/379000/378487/96c2bd35608e4891886a27ee38dd74ee.jpg,&109364=0,,3.9,664,/hotel/110000/109364/08256c20d56540038bcf33113035f40e.jpg,&457232=97935,210,4.2,1574,/hotel/129000/128590/7eb409e6508240268c3767c2d5558b0d.jpg,/hotel/98000/97935/93251B20-47C9-4D04-A266-F8C117D306D9.jpg; ticket_ctrip=uoeOwviAJ6VQEgTNwLuTqSV9j/bS+aOP3Riia1P+kyQbgkQZsD2giRixCDJ+4aMDOugOsFgRiIMeKX1EblTNpI+Q6wZZ/bsEyPxLAWbvJMuMwep4VGOFsQGJG/MajVq8l9iffe5rsQjliRr0UNOikYG0lhMJRZ/FKJ2ylZyd7z9LzESsSzQ4LA8NVswiaIp3f6zW5GwXj7yrbZwBfGqgF6pnoM1nPC33XGMMvYn6rHZklMAkX11Q8wDznTs6BhkOebrzAWfb0MMQI/fWsy7iXw==; CtripUserIdEx=89AC4B64BAC8C0B41219A92292272789D30A614DCF977B132DCAF3EC46E59103; CtripUserId=89AC4B64BAC8C0B45432AAB49F8D6DF6; corpid=; corpname=; CtripUserInfo=VipGrade=0&UserName=&NoReadMessageCount=0&U=6F76952242467DC1807D124EE9CF88BA; AHeadUserInfo=VipGrade=0&UserName=&NoReadMessageCount=0&U=6F76952242467DC1807D124EE9CF88BA; preferences=uid=M79046409&login_str=M79046409; SMBID=; LoginStatus=1%7c; login_type=0; login_uid=18010095515; auto=0B96E05F6D81E2403BA55359D8344AD4B8899A9BE8990DAF; ASP.NET_SessionId=xeruthhroorjlohdjsdufvgd"""

crawler = async_crawl.async_crawl()
crawler.setHeaders(Cookie=Cookie)

global citys, hotels
citys = {}
hotels = {}
setting = {
        "start_date": "2014-05-12",
        "dep_date": "2014-05-13",
        "website": "ctrip",
        "lengthofstay": 1,
        "send_email_time": {"hour": 2,
            "minute": 0,
            "second": 0,
            "frequency": 1}
        }

price_dict = {
        "0": "9",
        "1": "8",
        "2": "0",
        "3": "5",
        "4": "7",
        "5": "3",
        "6": "1",
        "7": "6",
        "8": "2",
        "9": "4"}


def start():
    url = "http://hotels.ctrip.com/Domestic/Tool/AjaxGetCitySuggestion.aspx"
    crawler.put({"url": url, "parse": parse_city, "result": {}})
    crawler.start(6)


def parse_city(text, result):
    global citys
    for lis in text.split('''",group''')[:-1]:
        citys[lis.split(r"""|""")[-1]] = lis.split("|")[-3].split('''"''')[-1].lower()
    # url_slice = ["http://hotels.ctrip.com/Domestic/Tool/AjaxFindKeyword.aspx?cityid=", "&keyword=%25u901F8&callback=cQuery.jsonpPosCallback"]
    url_slice = ["http://hotels.ctrip.com/hotel/", "/h39"]
    for key in citys:
        result = copy.copy(result)
        url = "".join([url_slice[0], "".join([citys[key], key]), url_slice[1]])
        result["_id"] = url
        result["city"] = citys[key]
        result["city_id"] = key
        crawler.put({"url": url, "parse": parse_hotel_code, "result": result}, 5)


def parse_hotel_code(text, result):
    try:
        soup = BeautifulSoup(text)
        if soup.find("div", {"id": "textNoresult"}):
            return
        url_slice = ["http://hotels.ctrip.com/Domestic/tool/AjaxHotelPriceNew.aspx?distinct=-1&city=",  # 0
                "&type=new&hotel=",  # 1
                "&&price=0-&RequestTravelMoney=F&promotion=F&prepay=F&IsCanReserve=F&IsJustConfirm=F&equip=&OrderBy=ctrip&OrderType=ASC&startDate=",  #2
                "&depDate=",  #3
                "&OrderBy=ctrip&OrderType=ASC&index=6&page=1&rs=1"]
        for item in soup.findAll("div", {"class": "searchresult_list"}):
            hotel_id = item["id"]
            result_ = copy.copy(result)
            result_["hotel"] = item.find("a", {"title": True})["title"]
            if u"速8" not in result_["hotel"]:
                continue
            url = "".join([
                url_slice[0],
                result_["city_id"],
                url_slice[1], hotel_id,
                url_slice[2], setting["start_date"],
                url_slice[3], setting["dep_date"],
                url_slice[4]
                ])
            result_["number"] = hotel_id
            crawler.put({"url": url, "parse": parse_house, "result": result_}, 6)
        if not result.get("already_page"):
            next_page = soup.find("div", {"class": "c_page_list layoutfix"})
            last_page = next_page.findAll("a")[-1].string
            if int(last_page) > 1:
                for page in range(2, int(last_page)+1):
                    result_ = copy.copy(result)
                    url = "".join([result["_id"], "p", str(page)])
                    print "next page:", url
                    result_["already_page"] = True
                    crawler.put({"url": url, "parse": parse_hotel_code, "result": result_}, 5)
    except:
        print traceback.print_exc()


def parse_hotel(text, result):
    hotels = {}
    if "Hotel@" not in text:
        return
    for item in text.split("|Hotel")[:-1]:
        hotels[item.split("|")[-1]] = item.split("|")[-2]
    url_slice = ["http://hotels.ctrip.com/Domestic/tool/AjaxHotelPriceNew.aspx?distinct=-1&city=",  # 0
            "&type=new&hotel=",  # 1
            "&&price=0-&RequestTravelMoney=F&promotion=F&prepay=F&IsCanReserve=F&IsJustConfirm=F&equip=&OrderBy=ctrip&OrderType=ASC&startDate=",  # 2
            "&depDate=",  # 3
            "&OrderBy=ctrip&OrderType=ASC&index=6&page=1&rs=1"]
    for key in hotels:
        result_ = copy.copy(result)
        url = "".join([url_slice[0],
            result["city_id"],
            url_slice[1], key,
            url_slice[2], setting["start_date"],
            url_slice[3], setting["dep_date"],
            url_slice[4]])
        result_["_id"] = url
        result_["hotel"] = hotels[key]
        crawler.put({"url": url, "parse": parse_house, "result": result_}, 10)


def parse_house(text, result):
    global csv_writer
    w = datetime.datetime.now() + datetime.timedelta(hours=8)
    try:
        soup = BeautifulSoup(text)
        tr_count = 0
        tr_all = soup.find("tbody").findAll("tr")
        for item in soup.findAll("tr", {"class": "t"}):
            # result["bed_type"] = item.find("td",
            #         {"class": "hotel_room_name"}).contents[0]    
            tds = item.findAll("td")
            result["room_name"] = item.find("a",
                    {"class": "hotel_room_name"}).contents[0]
            if len(tds) > 1:
                result["board_type"] = clear_tag(
                        str(tds[2].contents[0]))
                # result["board_type"] = tds[2].spancontents[0]
                result["price"] = clear_tag(
                        "".join(
                            [str(element) for element in item.find("span", {"class": "base_price"}).contents]))
                if item.find("span", {"class": "label_onsale_txt"}):
                    result["rebate"] = clear_tag(
                            "".join(
                                [str(element) for element in item.find("span", {"class": "label_onsale_txt"}).contents]
                                )
                            )
                else:
                    result["rebate"] = str(u"不返现")
                if item.find("a", {"class": "btn_buy"}):
                    result["availablity"] = str(u"1").encode("gb2312")
                elif item.find("a", {"class": "hotel_btn_view"}):
                    result["availablity"] = str(u"1").encode("gb2312")
                else:
                    result["availablity"] = str(u"0").encode("gb2312")
                csv_writer.writerow(
                        [str(w.strftime("%Y-%m-%d")),
                        setting["website"],
                        result["city"],
                        u"速8".encode("gb2312"),
                        result["number"],
                        result["hotel"].encode("gb2312"),
                        result["room_name"].encode("gb2312"),
                        setting["start_date"],
                        setting["lengthofstay"],
                        u"".encode("gb2312"),
                        result.get("price").split(";")[-1] if u"价" not in result.get("price") else -1,
                        result["rebate"].encode("gb2312"),
                        result["board_type"].encode("gb2312"),
                        result["availablity"]]
                        )
                del result["price"]
                del result["board_type"]
                del result["rebate"]
                del result["availablity"]
            elif len(tds) == 1:
                tr_count = tr_count + 1
                result["hotel_room_style"] = []
                result["price_arry"] = []
                result["availablity_arry"] = []
                result["rebate_arry"] = []
                result["board_type_arry"] = []
                while tr_all[tr_count]["class"] == "unexpanded":
                    item_ = tr_all[tr_count]
                    tr_count = tr_count + 1
                    tds = item_.findAll("td")
                    result["hotel_room_style"].append(
                            item_.find("span",
                            {"class": "hotel_room_style"}).contents[0]
                            )
                    result["board_type_arry"].append(
                            clear_tag(
                                str(tds[2].contents[0])
                            ))
                    price = clear_tag(
                            "".join(
                                [str(element) for element in item_.find("span", {"class": "base_price"}).contents]))
                    result["price_arry"].append("".join(price).split(";")[-1])
                    if item_.find("a", {"class": "btn_buy"}):
                        result["availablity_arry"].append(str(u"1"))
                    elif item_.find("a", {"class": "hotel_btn_view"}):
                        result["availablity_arry"].append(str(u"1"))
                    else:
                        result["availablity_arry"].append(str(u"0"))
                    if item_.find("span", {"class": "label_onsale_txt"}):
                        result["rebate_arry"].append(
                                clear_tag(
                                "".join(
                                    [str(element) for element in item_.find("span", {"class": "label_onsale_txt"}).contents])))
                    else:
                        result["rebate_arry"].append(str(u"不返现"))
                for (hotel_room_style,
                    price,
                    rebate,
                    board_type,
                    availablity) in zip(result["hotel_room_style"],
                                        result["price_arry"],
                                        result["rebate_arry"],
                                        result["board_type_arry"],
                                        result["availablity_arry"]):
                    csv_writer.writerow(
                            [w.strftime("%Y-%m-%d"),
                            setting["website"],
                            result["city"],
                            u"速8".encode("gb2312"),
                            result["number"],
                            result["hotel"].encode("gb2312"),
                            result["room_name"].encode("gb2312"),
                            setting["start_date"],
                            setting["lengthofstay"],
                            hotel_room_style.encode("gb2312"),
                            price if u"价" not in price else -1,
                            rebate.encode("gb2312"),
                            board_type.encode("gb2312"),
                            availablity.encode("gb2312")]
                            )
                del result["hotel_room_style"]
                del result["price_arry"]
                del result["availablity_arry"]
                del result["rebate_arry"]
                del result["board_type_arry"]
            tr_count = tr_count + 2
    except Exception, e:
        print e
        print traceback.print_exc()


def clear_tag(text):
    if "<" not in text:
        return text
    else:
        result = []
        for item in text.split("<"):
            if item.strip():
                result.append(item.split(">")[-1].strip())
        result = "".join([item for item in result])
        return result


global csv_writer


def main():
    global csv_writer
    now = datetime.datetime.now() + timedelta(hours=8) + timedelta(days=1)
    day = timedelta(days=1)
    setting["start_date"] = str(now.strftime("%Y-%m-%d"))
    setting["dep_date"] = str((now+day).strftime("%Y-%m-%d"))
    ofile = open("xiecheng%s.csv" % setting["start_date"], "w+")
    csv_writer = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
    csv_writer.writerow([
            u"报告日期".encode("gb2312"),
            u"渠道".encode("gb2312"),
            u"城市".encode("gb2312"),
            u"所属集团".encode("gb2312"),
            u"酒店代码".encode("gb2312"),
            u"酒店名称".encode("gb2312"),
            u"房型".encode("gb2312"),
            u"入住日期".encode("gb2312"),
            u"入住天数".encode("gb2312"),
            u"价格说明".encode("gb2312"),
            u"价格".encode("gb2312"),
            u"返现".encode("gb2312"),
            u"是否含早".encode("gb2312"),
            u"房态".encode("gb2312")
            ])
    start()
    print "################################################"
    ofile.close()
    crawler.finished.set()


def sendEmail():
    from send_email import email
    import os
    while True:
        crawler.finished.get()
        exmail = email()
        exmail.set_from("dazhuang@37degree.com")
        exmail.set_to("joe.xu@super8.com.cn")
        exmail.set_subject("xiecheng%s" % setting["start_date"])
        print os.getcwd()+"/xiecheng%s.csv" % setting["start_date"]
        exmail.add_attachment(os.getcwd()+"/xiecheng%s.csv" % setting["start_date"])
        exmail.send()
        # exmail.set_to("670108918@qq.com")
        # exmail.send()
        crawler.finished = AsyncResult()


def main_test():
    while True:
        print "------------------------------"
        gevent.sleep(20)


def schedule():
    from multiprocessing import Process
    while True:
        now = datetime.datetime.now() + datetime.timedelta(hours=8)
        tomorrow = now + datetime.timedelta(days=setting["send_email_time"]["frequency"]) + datetime.timedelta(hours=8)
        delta = datetime.datetime(year=tomorrow.year,
                month=tomorrow.month,
                day=tomorrow.day,
                hour=setting["send_email_time"]["hour"],
                minute=setting["send_email_time"]["minute"],
                second=setting["send_email_time"]["second"]) - now
        sleep_time = delta.total_seconds()
        main()
        print sleep_time, "sleep_time"
        print now
        print tomorrow
        gevent.sleep(sleep_time)


if __name__ == "__main__":
    g1 = gevent.spawn(schedule)
    g2 = gevent.spawn(main_test)
    g3 = gevent.spawn(sendEmail)
    gevent.joinall([g1, g2, g3])
