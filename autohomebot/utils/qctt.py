import json
import random
import re
from urllib import parse
import pymongo
import requests
import time
from selenium import webdriver
import redis
from lxml import etree
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


def get_proxie():
    # url = 'http://127.0.0.1:5555/random'  # API接口
    # r = requests.get(url, timeout=8)
    # if r.status_code == 200:
    #     ip = r.text
    #     # ip = ip.split(',')[0]
    #     if ip == None:
    #         time.sleep(1)
    #         return get_proxie()
    #     else:
    #         return ip
    # else:
    #     time.sleep(1)
    #     return get_proxie()
    list = ['47.92.126.49:16816','39.96.209.21:16816','47.92.129.191:16816']
    ip = random.choice(list)
    return ip

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--proxy-server={}'.format(get_proxie()))
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 禁止图片加载
browser = webdriver.Chrome(chrome_options=chrome_options)
# browser.set_page_load_timeout(3)
browser.implicitly_wait(10)

# mongo设置
MONGO_URL = 'localhost'
MONGO_DB = 'qctt'
MONGO_COLLECTION = 'qctt'
_client = pymongo.MongoClient(MONGO_URL)
_dbMongo = _client[MONGO_DB]


# redis设置
KEY = "qcttNewsUrls"
redisPool = redis.ConnectionPool( host='localhost', port=6379, db=1, decode_responses = True)
_redisdb = redis.Redis(connection_pool=redisPool)


# 起始时间设置
START_TIME = "2017-01-01"
# def get_web_page(url):
#     while True:
#         try:
#             time.sleep(3)
#             html = requests.get(url, headers=headers)
#             if html.status_code == 404:
#                 return None
#             elif html.status_code != 200:
#                 print(url, html.status_code)
#                 continue
#             return html
#
#         except Exception as e:
#             print(e)



def get_web_page(url):
    while True:
        try:
            time.sleep(5)
            global browser
            browser.get(url)
            # located = (By.TAG_NAME,'textarea')
            # WebDriverWait(browser,20,0.5).until(EC.presence_of_all_elements_located(located))
            html = browser.page_source
            if "404" in html:
                return None
            if "汽车头条" not in html:
                browser.quit()
                chrome_options = webdriver.ChromeOptions()
                # chrome_options.add_argument('--headless')
                chrome_options.add_argument('--proxy-server={}'.format(get_proxie()))
                chrome_options.add_argument('--ignore-certificate-errors')
                chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
                chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 禁止图片加载
                browser = webdriver.Chrome(chrome_options=chrome_options)
                # browser.set_page_load_timeout(3)
                browser.implicitly_wait(10)
                continue
            while True:
                try:
                    more = browser.find_element_by_xpath('//div[@class="more_btn"]')
                    if more:
                        more.click()
                        time.sleep(1)
                        try:
                            # browser.switch_to.window(browser.window_handles().iterator().next())
                            alert = browser.switch_to.alert
                            alert.accept()
                            html = browser.page_source
                            return html
                        except:
                            continue
                except:
                    break
            return html
        except Exception as e:
            print(e)
            browser.quit()
            chrome_options = webdriver.ChromeOptions()
            # chrome_options.add_argument('--headless')
            chrome_options.add_argument('--proxy-server={}'.format(get_proxie()))
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 禁止图片加载
            browser = webdriver.Chrome(chrome_options=chrome_options)
            # browser.set_page_load_timeout(5)
            browser.implicitly_wait(10)


def get_url_list(url):
    while True:
        try:
            browser.get(url)
            time.sleep(2)
            html = browser.page_source
            doc = etree.HTML(html)
            body = doc.xpath('//body/text()')[0]
            try:
                doc = json.loads(body)
            except:
                continue
            return doc
        except:
            pass


def get_news_url(list):
    # 获取新闻url
    for item in list:
        # title = item['title']
        # publish_time = item['publish_time']
        # username = item['author_name']
        new_id = item['new_id']
        url = 'https://www.qctt.cn/news/{}'.format(new_id)
        _redisdb.sadd(KEY,url)


def get_web_comments(url):
    # 根据新闻id获取评论
    html = get_web_page(url)
    print(url)
    if not html:
        return None
    doc = etree.HTML(html)
    # 标题
    try:
        title = doc.xpath('//*[@class="title"]/text()')[0]
    except:
        return None
    # 发表时间
    try:
        push_time = doc.xpath('//div[@class="part2"]/span[last()-1]/text()')[0]
    except:
        return None
    # 作者&来源
    try:
        author = doc.xpath('//div[@class="part2"]/a/text()')[0]
        if not author:
            author = doc.xpath('//div[@class="part2"]/span[1]/text()')[0]
    except:
        author = None
        pass
    # 正文
    try:
        content_path = doc.xpath('//div[@class="y_text" or @class="y_text2"]')[0]
        content = content_path.xpath('string(.)')
    except:
        content = None
    item = {}
    item['title'] = title
    item['bbs_name'] = '汽车头条'
    item['sonbbs_name'] = None
    item['username'] = author
    item['comment_detail'] = content
    item['comment_url'] = url
    item['push_time'] = push_time
    item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    item['car_type'] = None
    item['collection'] = "汽车头条"  # 设置存入表名
    item['usergender'] = None
    item['userlocation'] = None
    item['userage'] = None
    _dbMongo[MONGO_COLLECTION].insert(dict(item))

    # 获取评论
    try:
        comments = doc.xpath('//div[@class="comment clearfix"][@new_index]')
        if comments != []:
            for comment in comments:
                username = comment.xpath('./div[@class="comment_right fl"]/div[1]/span[1]/text()')[0]
                push_time = comment.xpath('./div[@class="comment_right fl"]/div[1]/span[2]/text()')[0]
                try:
                    content = comment.xpath('./div[@class="comment_right fl"]/div[2]/text()')[0]
                except:
                    continue
                item['username'] = username
                item['comment_detail'] = content
                item['push_time'] = push_time
                _dbMongo[MONGO_COLLECTION].insert(dict(item))
    except Exception as e:
        print(e.__traceback__.tb_lineno,e)



if __name__ == '__main__':
    # 搜索关键字获取新闻列表
    # KW_LIST = [
    #     "自动驾驶", "无人驾驶", "智能网联汽车",
    #     "L3级别", "L4级别",
    #     "无人", "视觉融合",
    #     "V2X", "激光雷达",
    #     "高精度地图", "AI自动驾驶",
    #     "算法", "自动驾驶牌照", "示范区",
    #     "示范运营", "自动泊车", "智慧交通",
    #     "5G", "智能化"
    # ]
    # url_lsit = []
    # for kw in KW_LIST:
    #     kw = parse.quote(kw)
    #     page = 1
    #     while page < 51:
    #         url = "https://www.qctt.cn/news_result_loadmore?keyword={}&page={}".format(kw,page)
    #         print(url)
    #         text = get_url_list(url)
    #         if text:
    #             get_news_url(text)
    #         else:
    #             break
    #         page += 1

    # 通过链接爬取评论
    url = _redisdb.spop(KEY)
    # url = url.repalce('www','m')
    while url:
        get_web_comments(url)
        # get_mobile_comments(url)
        url = _redisdb.spop(KEY)


