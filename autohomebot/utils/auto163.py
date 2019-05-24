import json
import random
import re
import pymongo
import requests
import time
from selenium import webdriver
import redis
from lxml import etree

# chrome_options = webdriver.ChromeOptions()
# # chrome_options.add_argument('--headless')
# # chrome_options.add_argument('--proxy-server=10.172.226.35:8080')
# chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
# # chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 禁止图片加载
# browser = webdriver.Chrome(chrome_options=chrome_options)


# mongo设置
MONGO_URL = 'localhost'
MONGO_DB = 'auto163'
MONGO_COLLECTION = 'auto163'
_client = pymongo.MongoClient(MONGO_URL)
_dbMongo = _client[MONGO_DB]


# redis设置
KEY = "163NewsUrls"
redisPool = redis.ConnectionPool( host='localhost', port=6379, db=1, decode_responses = True)
_redisdb = redis.Redis(connection_pool=redisPool)

# 起始时间设置
START_TIME = "2017-01-01"

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }
def get_web_page(url):
    # 获取新闻列表页
    while True:
        try:
            html = requests.get(url,headers=headers)
            if html.status_code == 200:
                return html.text
            if html.status_code == 404:
                return None
            else:
                print(url, html.status_code)
                return None
        except Exception as e:
            print(e)
            return None
# def get_web_page(url):
#     while True:
#         try:
#             browser.get(url)
#             break
#         except:
#             pass
#     browser.implicitly_wait(10)
#     js = "var q=document.documentElement.scrollTop=10000"
#     # 执行脚本
#     browser.execute_script(js)
#     time.sleep(1.5 * random.uniform(1, 3))
#     html = browser.page_source
#     while "您的访问出现异常" in html:
#         print("出现验证，休眠")
#         time.sleep(1 * 60)
#         browser.get(url)
#         html = browser.page_source
#     return html

def get_news_url(html):
    # 获取新闻url
    doc = etree.HTML(html)
    urls = doc.xpath('//*[starts-with(@class,"sec-list-item auto_news_item")]/a/@href')
    for url in urls:
        _redisdb.sadd(KEY,url)
    try:
        next_page = doc.xpath('//a[@class="ac_pages_next"]/@href')[0]
        if "http://" in next_page:
            next_page = next_page.replace('\\','/')
            html = get_web_page(next_page)
            if html:
                get_news_url(html)
    except Exception as e:
        print("无下一页",e.__traceback__.tb_lineno,e)


def get_comments(url):
    # 根据新闻id获取评论
    html = get_web_page(url)
    if not html:
        return None
    doc = etree.HTML(html)
    try:
        title = doc.xpath('//h1/text()')[0]
    except:
        return None
    id = re.search(r'//.*/(.*?)\.html',url).group(1)
    pg = 0
    while True:
        offset = 30 * pg  # 自增数为30
        comt_url = "http://comment.api.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/{}/comments/newList?ibc=newspc&limit=30&showLevelThreshold=72&headLimit=1&tailLimit=2&offset={}".format(
            id, offset)
        print(url,"第{}页".format(pg))
        time.sleep(2)
        response = requests.get(comt_url, headers=headers)
        html = response.text
        doc = json.loads(html)
        try:
            data = doc["comments"]
            if data == {}:
                print("全部完成")
                break
            for key in data:
                if not key:
                    print("无数据")
                    break
                item = {}
                try:
                    username = data[key]['user']['nickname']
                except:
                    username = None
                try:
                    comment_detail = data[key]['content']
                except:
                    comment_detail = None
                try:
                    push_time = data[key]["createTime"]
                    if push_time < START_TIME:
                        print("时间截止")
                        break
                except:
                    push_time = None

                item['title'] = title
                item['bbs_name'] = '网易汽车'
                item['sonbbs_name'] = None
                item['username'] = username
                item['comment_detail'] = comment_detail
                item['comment_url'] = url
                item['push_time'] = push_time
                item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item['car_type'] = None
                item['collection'] = "(汽车之家问答)自动驾驶"  # 设置存入表名
                item['usergender'] = None
                item['userlocation'] = None
                item['userage'] = None
                _dbMongo[MONGO_COLLECTION].insert(dict(item))
        except Exception as e:
            print(e, "无数据")
            break
        pg += 1


if __name__ == '__main__':
    # # 从各大板块获取新闻链接
    # url_list = [
    #     'https://auto.163.com/buy/',
    #     'https://auto.163.com/newcar/',
    #     'https://auto.163.com/test/',
    #     'https://auto.163.com/guide/',
    #     'https://auto.163.com/chezhu/',
    #     'http://auto.163.com/special/auto_newenergy/',
    #     'https://auto.163.com/news/',
    #     'https://auto.163.com/special/carlife/'
    # ]
    # for url in url_list:
    #     html = get_web_page(url)
    #     get_news_url(html)

    # 通过链接爬取评论
    url = _redisdb.spop(KEY)
    while url:
        get_comments(url)
        url = _redisdb.spop(KEY)
