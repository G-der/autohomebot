# coding=utf-8
import json
import random
import re
import time
import requests
from scrapy.http import HtmlResponse as hr
from selenium import webdriver
from selenium.common.exceptions import  TimeoutException
import redis
import pymongo
from lxml import etree
from autohomebot.items import ProduceItem
from dateutil.parser import parse
import pymssql


START_TIME = "2018-01-01"
MAX_PAGE = 100
search_dict = {
    "机油": "https://s.taobao.com/search?ie=utf8&initiative_id=staobaoz_20190401&stats_click=search_radio_all%3A1&js=1&imgfile=&q=%E6%9C%BA%E6%B2%B9&suggest=history_1&_input_charset=utf-8&wq=&suggest_query=&source=suggest&cps=yes&ppath=20000%3A133794%3B20000%3A133795%3B20000%3A133796",
    "机滤": "https://s.taobao.com/search?q=%E6%9C%BA%E6%B2%B9%E6%BB%A4%E6%B8%85%E5%99%A8&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20190401&ie=utf8&cps=yes&ppath=20000%3A3223459%3B20000%3A46748%3B20000%3A3395409",
    "雨刷": "https://s.taobao.com/search?q=%E9%9B%A8%E5%88%AE%E5%99%A8&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20190401&ie=utf8&cps=yes&ppath=20000%3A16172685%3B20000%3A3223459%3B20000%3A27961",
    "冷冻液": "https://s.taobao.com/search?spm=a21bo.7723600.8571.106.66ee5ec9T4XQhT&cat=50032518&bcoffset=-291&ntoffset=-291&p4ppushleft=1%2C48",
    "电池": "https://s.taobao.com/search?q=%E6%B1%BD%E8%BD%A6%E8%93%84%E7%94%B5%E6%B1%A0&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20190401&ie=utf8&cps=yes&ppath=20000%3A4535364%3B20000%3A786014378%3B20000%3A3223459",
    "轮胎": "https://s.taobao.com/search?q=%E6%B1%BD%E8%BD%A6%E8%BD%AE%E8%83%8E&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20190401&ie=utf8",
    "车灯": "https://s.taobao.com/search?ie=utf8&initiative_id=staobaoz_20190401&stats_click=search_radio_all%3A1&js=1&imgfile=&q=%E6%B1%BD%E8%BD%A6%E5%A4%A7%E7%81%AF%E7%81%AF%E6%B3%A1&suggest=history_1&_input_charset=utf-8&wq=&suggest_query=&source=suggest&cps=yes&ppath=20000%3A10246%3B20000%3A100291",
    "刹车油": "https://s.taobao.com/search?q=%E5%88%B9%E8%BD%A6%E6%B2%B9&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20190401&ie=utf8&cps=yes&ppath=20000%3A3223459%3B20000%3A3769220",
    "空气滤": "https://s.taobao.com/search?q=%E7%A9%BA%E6%B0%94%E6%BB%A4%E6%B8%85%E5%99%A8&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20190401&ie=utf8&cps=yes&ppath=20000%3A3223459%3B20000%3A46748%3B20000%3A3395409",
    "刹车盘": "https://s.taobao.com/search?q=%E5%88%B9%E8%BD%A6%E7%9B%98&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20190401&ie=utf8&cps=yes&ppath=20000%3A3769220%3B20000%3A83156602",
    "火花塞": "https://s.taobao.com/search?q=%E7%81%AB%E8%8A%B1%E5%A1%9E&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20190401&ie=utf8&cps=yes&ppath=20000%3A121501198%3B20000%3A3487894%3B20000%3A3223459",
    "刹车片": "https://s.taobao.com/search?q=%E5%88%B9%E8%BD%A6%E7%89%87&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20190401&ie=utf8&cps=yes&ppath=20000%3A3223459%3B20000%3A3769220%3B20000%3A83156602",
    "变速箱油": "https://s.taobao.com/search?q=%E5%8F%98%E9%80%9F%E7%AE%B1%E6%B2%B9&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20190401&ie=utf8&cps=yes&ppath=20000%3A133795%3B20000%3A3223459%3B20000%3A3223486",
    "空调滤清器": "https://s.taobao.com/search?q=%E7%A9%BA%E8%B0%83%E6%BB%A4%E6%B8%85%E5%99%A8&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20190401&ie=utf8&cps=yes&ppath=20000%3A3223459%3B20000%3A46748%3B20000%3A3395409",
    "正时皮带": "https://s.taobao.com/search?q=%E6%AD%A3%E6%97%B6%E7%9A%AE%E5%B8%A6&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20190401&ie=utf8&cps=yes&ppath=20000%3A3562983%3B20000%3A3227284"
}
PROGRAME_STARTTIME = parse(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

# MongoDB抓取结果存储数据库
MONGO_URL = 'absit1309'
MONGO_DB = 'taobao'
MONGO_COLLECTION = None
_client = pymongo.MongoClient(MONGO_URL)
_dbMongo = _client[MONGO_DB]

# RedisDB抓取URLS存储数据库
redisPool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True, db=1)
_dbRedis = redis.Redis(connection_pool=redisPool)

# sqlserver读取连接
HOST = "ABSIT1302\SQL2012"
USER = "sa"
PW = "12345678"
SQL_DB = "Crawler"

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--proxy-server=10.172.226.35:8080')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
# chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 禁止图片加载
browser = webdriver.Chrome(chrome_options=chrome_options)
browser.implicitly_wait(10)


def CreateSearchUrl(key, url, page):
    """生成商品链接"""
    try:
        searchUrl = url + "&s={}".format(page)
        print('以关键字所查询的结果的前{}页商品的URLS:'.format(MAX_PAGE), searchUrl)
        _dbRedis.sadd("TB{}searchResultUrls".format(key), searchUrl)
    except TimeoutException:
        CreateSearchUrl(key, url, page)


def CreateProductDetailUrl(key):
    """
    遍历搜索页面
    """
    search_url = _dbRedis.spop('TB{}searchResultUrls'.format(key))
    while search_url:  # 当数据库还存在网页url，取出一个并爬取
        # now = parse(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        # global PROGRAME_STARTTIME
        # if (now - PROGRAME_STARTTIME).seconds >= 3600:
        #     print("连续抓取一小时，休息10分钟")
        #     time.sleep(10 * 60)
        #     PROGRAME_STARTTIME = parse(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        SaveProductDetailUrl(key, search_url)
        search_url = _dbRedis.spop('TB{}searchResultUrls'.format(key))
        time.sleep(0.5)


def SaveProductDetailUrl(key, url):
    """
    保存商品链接
    """
    browser.get(url)
    # if "亲，小二正忙，滑动一下马上回来" in browser.page_source:
    #     while True:
    #         try:
    #             # 定位滑块元素
    #             source = browser.find_element_by_xpath("//*[@id='nc_1_n1z']")
    #             # 定义鼠标拖放动作
    #             ActionChains(browser).drag_and_drop_by_offset(source, 400, 0).perform()
    #             # 等待JS认证运行,如果不等待容易报错
    #             time.sleep(2)
    #             # 查看是否认证成功，获取text值
    #             text = browser.find_element_by_xpath("//*[@class='nc-lang-cnt']/span")
    #             # 目前只碰到3种情况：成功（请在在下方输入验证码,请点击图）；无响应（请按住滑块拖动)；失败（哎呀，失败了，请刷新）
    #             if text.text.startswith(u'哎呀，出错了'):
    #                 continue
    #             else:
    #                 break
    #         except Exception as e:
    #             # 这里定位失败后的刷新按钮，重新加载滑块模块
    #             browser.find_element_by_link_text("刷新").click()
    #             print(e)
    # 生成移动脚本
    js = "var q=document.documentElement.scrollTop=10000"
    # 执行脚本
    browser.execute_script(js)
    # 等待页面加载
    time.sleep(10)
    # 隐式等待元素加载
    browser.implicitly_wait(10)

    html = browser.page_source
    if "未找到" in browser.page_source:
        return
    doc = etree.HTML(html)
    items = doc.xpath('//div[@class="item J_MouserOnverReq  "]')
    for item in items:
        product_url = item.xpath('.//div[@class="row row-2 title"]/a/@href')[0]
        productDetailUrl = 'https:' + product_url
        print('正在生成各商品详细信息的URLS:', productDetailUrl)
        _dbRedis.sadd("TB{}DetailUrls".format(key), productDetailUrl)


def Get_content(key):
    """从redis读取url"""
    # url = _dbRedis.spop("TB{}DetailUrls".format(key))
    url = 'https://detail.tmall.com/item.htm?spm=a230r.1.14.1.3f195228YlslIJ&id=40880131694&ns=1&abbucket=17'
    while url:
        parse_main(key, url)
        url = _dbRedis.spop("TB{}DetailUrls".format(key))
        time.sleep(1)
    """从sql读取url"""
    # with pymssql.connect(HOST, USER, PW, SQL_DB) as conn:
    #     with conn.cursor(as_dict=True) as cursor:
    #         cursor.execute("SELECT distinct [product_name],[detail_url] FROM [Crawler].[dbo].[TBD_Taobao] where [product_name] like N'%车灯%'")
    #         for row in cursor:
    #             # print("ID=%d, Name=%s" % (row['id'], row['name']))
    #             url = row['detail_url']
    #             parse_main(key, url)


def parse_main(key, url):
    print("正在抓取", url, "的数据")
    try:
        while True:
            browser.refresh()
            try:
                browser.get(url)
            except TimeoutException:
                print("获取网页超时，重试")
                continue
            rs = hr(browser.current_url, body=browser.page_source, encoding="utf-8")
            # str_stop_Xpath = "//div[@id='J_sufei']//iframe | //iframe[starts-with(@id,'sufei-dialog-content')]"  #| //div[starts-with(@id,'ks-component')]
            # # hidden = rs.xpath(str_stop_Xpath).xpath('./@class').extract_first()
            # #             # if hidden == "ks-overlay ks-imagezoom-viewer ks-overlay-hidden":
            # #             #     print('验证被隐藏')
            # #             #     break
            # if rs.xpath(str_stop_Xpath):
            #     print("[1]【{}】有验证，休眠后重试".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
            #     time.sleep(300)
            # else:
            break
        html = browser.page_source
        doc = etree.HTML(html)
        item = ProduceItem()
        # 店铺名
        try:
            shop_path = doc.xpath('//*[@class="tb-shop-name" or @class="slogo-shopname" or @class="shop-name"]')[0]
            shopname = shop_path.xpath('string(.)').strip()
        except:
            shopname = None
        item['shopname'] = shopname
        # 品牌
        try:
            brand = doc.xpath('//*[@class="attributes-list"]//*[contains(text(),"品牌")]/@title')[0]
        except:
            brand = None
        item['brand'] = brand
        # 商品标题
        try:
            title_path = doc.xpath('//h3[@class="tb-main-title"]/@data-title | //div[@class="tb-detail-hd"]//h1/text()')[0]
        except:
            title_path = None
        item['productTitle'] = title_path
        # 商品价格
        try:
            price = doc.xpath('//*[@id="J_StrPriceModBox"]//*[@class="tb-rmb-num" or @class="tm-price"]/text()')
            # print(price[0])
            item['productPrice'] = price[0]
        except:
            item['productPrice'] = None

        item['data_from'] = "淘宝"
        item['productName'] = key
        item['productDetailUrl'] = browser.current_url
        item['productID'] = re.search(r'id=(\d+)', browser.current_url).group(1)
        cookies = browser.get_cookies()
        ck = ""
        for cookie in cookies:
            ck += cookie['name'] + "=" + cookie['value'] + '; '
        # print(ck)
        if browser.current_url.startswith("https://item"):
            if doc.xpath('//*[@class="J_ReviewsCount"]/text()')[0] != '0':
                Get_Comment_TB(item, ck)
        else:
            if ''.join(rs.xpath("//li[@id='J_ItemRates']//span[@class='tm-count']/text()").extract()).strip() != '0':
                sellerid = doc.xpath('//*[@id="dsr-userid"]/@value')[0]
                item['allCount'] = ''.join(rs.xpath("//li[@id='J_ItemRates']//span[@class='tm-count']/text()").extract()).strip()
                Get_Comment_TM(item, ck, sellerid)
    except Exception as e:
        print(e.__traceback__.tb_lineno, e)


def Get_Comment_TB(item, cookie):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        'cookie': cookie
    }
    id = item['productID']
    try:
        # 商品评论
        main_url = "https://rate.taobao.com/detailCommon.htm?auctionNumId={}".format(
            id)
        while True:
            try:
                time.sleep(5 * random.uniform(1, 1.5))
                response = requests.get(main_url, headers=headers, timeout=3, allow_redirects=False)
            except Exception as e:
                print("请求评论数错误:", e, "重试")
                continue
            # print(response.text)
            data = None
            if response.text:
                dic = re.search(r'\((.*)\)', response.text)
                if dic:
                    dic = dic.group(1)
                    data = json.loads(dic)
                elif re.search(r'rgv587_flag', response.text):
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), '被反爬，休眠后重试')
                    time.sleep(300)
                    # browser.refresh()
                    browser.get(browser.current_url)
                    browser.implicitly_wait(10)
                    cookies = browser.get_cookies()
                    ck = ""
                    for cookie in cookies:
                        ck += cookie['name'] + "=" + cookie['value'] + '; '
                    headers['cookie'] = ck
                    continue
                else:
                    print(response.text)
            if not data:
                browser.refresh()
                browser.implicitly_wait(10)
                # browser.get(main_url)
                # comt_link = browser.find_element_by_xpath("//a[contains(text(),'累计评')]")
                # browser.execute_script("arguments[0].click()", comt_link)
                rs = hr(browser.current_url, body=browser.page_source, encoding="utf-8")
                str_stop_Xpath = "//div[@id='J_sufei']//iframe | //iframe[starts-with(@id,'sufei-dialog-content')]"
                # hidden = rs.xpath(str_stop_Xpath).xpath('./@class').extract_first()
                # if hidden == "ks-overlay ks-imagezoom-viewer ks-overlay-hidden":
                #     print('验证被隐藏')
                #     break
                if rs.xpath(str_stop_Xpath):
                # if "休息会呗" in browser.page_source:
                    # self.logger.error("STOP_URL:" + str_stop_Xpath + "|" + pnum + ":" + u)
                    print("[2]【{}】有验证，休眠后重试".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                    # time.sleep(300)
                    continue
                else:
                    print("无验证,无数据")
                    break
            break
        count = data["data"]["count"]
        item['allCount'] = count["totalFull"]
        item['haopingCount'] = count["good"]
        item['zhongpingCount'] = count["normal"]
        item['chapingCount'] = count["bad"]
        req = {}
        if item["haopingCount"] != 0:
            req["好评"] = 1
        if item["zhongpingCount"] != 0:
            req["中评"] = 0
        if item["chapingCount"] != 0:
            req["差评"] = -1
        if req is {}:
            print("该商品暂无评论")
            return
        for key, value in req.items():
            pg = 1
            max_page = 2
            while pg <= max_page:
                time_switch = False
                time.sleep(5 * random.uniform(1, 1.5))
                comt_url = "https://rate.taobao.com/feedRateList.htm?auctionNumId={}&currentPageNum={}&pageSize=20&rateType={}&orderType=feedbackdate&folded=0".format(
                    id, pg, value)
                print(comt_url, key, "第{}页".format(pg))
                try:
                    response = requests.get(comt_url, headers=headers, timeout=3, allow_redirects=False)
                except Exception as e:
                    print("请求评论详情错误:", e, "重试")
                    continue
                data = None
                if response.text:
                    dic = re.search(r'\((.*)\)', response.text)
                    if dic:
                        dic = dic.group(1)
                        data = json.loads(dic)
                    elif re.search(r'rgv587_flag', response.text):
                        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), '被反爬，休眠后重试')
                        time.sleep(300)
                        browser.get(browser.current_url)
                        # browser.refresh()
                        browser.implicitly_wait(10)
                        cookies = browser.get_cookies()
                        ck = ""
                        for cookie in cookies:
                            ck += cookie['name'] + "=" + cookie['value'] + '; '
                        headers['cookie'] = ck
                        continue
                    else:
                        print(response.text)
                if not data or data['comments'] == 'null' or data['comments'] == '[]':
                    browser.refresh()
                    # browser.get(comt_url)
                    browser.implicitly_wait(10)
                    # comt_link = browser.find_element_by_xpath("//a[contains(text(),'累计评')]")
                    # browser.execute_script("arguments[0].click()", comt_link)
                    rs = hr(browser.current_url, body=browser.page_source, encoding="utf-8")
                    str_stop_Xpath = "//div[@id='J_sufei']//iframe | //iframe[starts-with(@id,'sufei-dialog-content')]"
                    # hidden = rs.xpath(str_stop_Xpath).xpath('./@class').extract_first()
                    # if hidden == "ks-overlay ks-imagezoom-viewer ks-overlay-hidden":
                    #     print('验证被隐藏')
                    #     break
                    #
                    if rs.xpath(str_stop_Xpath):
                    # if "休息会呗" in browser.page_source:
                        # self.logger.error("STOP_URL:" + str_stop_Xpath + "|" + pnum + ":" + u)
                        print("[3]【{}】有验证，休眠后重试".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                        time.sleep(300)
                        continue
                    else:
                        print("无验证,无数据")
                        break
                total = data["total"]
                if total == 0:
                    print("无详细评价")
                    break
                max_page = data["maxPage"]
                if max_page == pg:
                    print("已到最后一页")
                    break
                comments = data["comments"]
                for comment in comments:
                    item['userInfo'] = comment['user']['nick']
                    date = time.strptime(comment['date'], "%Y年%m月%d日 %H:%M")
                    date_format = time.strftime("%Y-%m-%d %H:%M", date)
                    item['orderInfoTime'] = date_format
                    if item['orderInfoTime'] < START_TIME:
                        print("时间截止")
                        time_switch = True
                        break
                    item['orderInfoTitle'] = comment['auction']['sku']
                    item['comment_con'] = comment['content']
                    item["catch_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    Save_to_mongo(item['productName'], item)
                if time_switch:
                    break
                pg += 1
    except Exception as e:
        print("解析出错：", e.__traceback__.tb_lineno, e)


def Get_Comment_TM(item, cookie, sellerid):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        'cookie': cookie
    }
    id = item['productID']
    try:
        # 商品评论
        page = 1
        max_page = 1
        time_switch = False
        while page <= max_page:
            time.sleep(5 * random.uniform(1, 1.5))
            main_url = "https://rate.tmall.com/list_detail_rate.htm?itemId={}&sellerId={}&order=1&currentPage={}&append=0&content=1".format(
                id, sellerid, page)
            print("正在抓取第{}页".format(page))
            try:
                response = requests.get(main_url, headers=headers, timeout=3, allow_redirects=False)
            except Exception as e:
                print("请求评论数错误:", e, "重试")
                continue
            # print(response.text)
            data = None
            if response.text:
                dic = re.search(r'\((.*)\)', response.text)
                if dic:
                    dic = dic.group(1)
                    data = json.loads(dic)
                elif re.search(r'rgv587_flag', response.text):
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), '被反爬，休眠后重试')
                    time.sleep(300)
                    # browser.refresh()
                    browser.get(browser.current_url)
                    cookies = browser.get_cookies()
                    ck = ""
                    for cookie in cookies:
                        ck += cookie['name'] + "=" + cookie['value'] + '; '
                    headers['cookie'] = ck
                    continue
                else:
                    print(response.text)
            if not data:
                browser.refresh()
                # browser.get(main_url)
                browser.implicitly_wait(10)
                # comt_link = browser.find_element_by_xpath("//a[contains(text(),'累计评')]")
                # browser.execute_script("arguments[0].click()", comt_link)
                rs = hr(browser.current_url, body=browser.page_source, encoding="utf-8")
                str_stop_Xpath = "//div[@id='J_sufei']//iframe | //iframe[starts-with(@id,'sufei-dialog-content')]"
                # hidden = rs.xpath(str_stop_Xpath).xpath('./@class').extract_first()
                # if hidden == "ks-overlay ks-imagezoom-viewer ks-overlay-hidden":
                #     print('验证被隐藏')
                #     break
                if rs.xpath(str_stop_Xpath):
                # if "休息会呗" in browser.page_source:
                    # self.logger.error("STOP_URL:" + str_stop_Xpath + "|" + pnum + ":" + u)
                    print("[4]【{}】有验证，休眠后重试".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                    time.sleep(300)
                    continue
                else:
                    print("无验证,无数据")
                    break
            max_page = data['rateDetail']["paginator"]["lastPage"]
            comments = data['rateDetail']["rateList"]
            for comment in comments:
                item['userInfo'] = comment['displayUserNick']
                item['orderInfoTime'] = comment['rateDate']
                if item['orderInfoTime'] < START_TIME:
                    print("时间截止")
                    time_switch = True
                    break
                item['orderInfoTitle'] = item['productTitle']
                item['comment_con'] = comment['rateContent']
                item["catch_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                # item['allCount'] = data['rateDetail']["rateCount"]["total"]
                item['haopingCount'] = None
                item['zhongpingCount'] = None
                item['chapingCount'] = None
                Save_to_mongo(item['productName'], item)
            if time_switch:
                break
            page += 1
    except Exception as e:
        print("解析出错：", e.__traceback__.tb_lineno, e)


def Save_to_mongo(key, item):
    """
    保存至MongoDB
    :param result: 结果
    """
    MONGO_COLLECTION = key
    try:
        _dbMongo[MONGO_COLLECTION].insert(dict(item))
        # print('存储到MongoDB成功')
    except Exception:
        print('存储到MongoDB失败')


def login():
    start_url = "https://login.taobao.com/"
    browser.get(start_url)
    browser.implicitly_wait(10)
    while True:
        time.sleep(30)
        # if "手机扫码，安全登录" in browser.page_source:
        #     # print("请扫码登录")
        #     print("点击密码登录")
        #     try:
        #         browser.find_element_by_link_text("密码登录").click()
        #         browser.implicitly_wait(10)
        #     except NoSuchElementException:
        #         pass
        #     # continue
        # if "忘记密码" in browser.page_source:
        #     user_name = browser.find_element_by_id("TPL_username_1")
        #     # user_name.click()
        #     # browser.execute_script("arguments[0].value='八爪鱼20181025'", user_name)
        #     user_name.clear()
        #     user_name.send_keys(u'八爪鱼20181025')
        #     time.sleep(1.5)
        #     password = browser.find_element_by_id("TPL_password_1")
        #     password.clear()
        #     password.send_keys(u"tako2018")
        #     time.sleep(1.5)
        # if browser.find_element_by_id("J_SubmitStatic"):
        #     # browser.find_element_by_id("J_SubmitStatic").click()
        #     try:
        #         browser.find_element_by_id("J_SubmitStatic").send_keys(Keys.ENTER)
        #         browser.implicitly_wait(10)
        #     except NoSuchElementException:
        #         print("未定位到登录按钮")
        if browser.current_url != start_url:
            print("登录成功")
            break


def main():
    """
    淘宝评论抓取
    """
    # login()
    # for key, url in search_dict.items():
    #     # 创建URL
    #     # for pageInx in range(1, MAX_PAGE + 1):
    #         # # 淘宝的分布增长为0，44，88，132
    #         # pageInx = 44 * (pageInx - 1)
    #         # # 创建url
    #         # CreateSearchUrl(key, url, pageInx)
    #         #
    #         # # 所有商品详细内容URL
    #         # CreateProductDetailUrl(key)
    #
    #     # 抓取界面内容
    key = "沙拉酱"
    Get_content(key)
    browser.close()


""" 
程序入口
"""
if __name__ == '__main__':
    main()
