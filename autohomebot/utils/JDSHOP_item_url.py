# coding=utf-8
import json
import random
import re
import time
from urllib.parse import quote
import pandas as pd
import pymongo
import redis
from lxml import etree
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from autohomebot.items import ProduceItem
import requests


MONGO_URL = 'absit1309'
MONGO_DB = 'jingdong'
MONGO_COLLECTION = 'test'
START_TIME = "2018-01-01"
MAX_PAGE = 1

# MongoDB抓取结果存储数据库
_client = pymongo.MongoClient(MONGO_URL)
_dbMongo = _client[MONGO_DB]

# RedisDB抓取URLS存储数据库
redisPool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
_dbRedis = redis.Redis(connection_pool=redisPool)

# path_to_chromedriver='D:/Program Files/Python36/Scripts/chromedriver.exe'
chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
prefs ={
     'profile.default_content_setting_values': {
        'images': 2,
        # 'javascript':2
    }
}
chrome_options.add_experimental_option('prefs', prefs)  # 禁止图片加载
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
browser = webdriver.Chrome(chrome_options=chrome_options,
                           # executable_path=path_to_chromedriver
                           )
browser.implicitly_wait(10)



def Save_to_mongo(name,itemInfo):
    """
    保存至MongoDB
    :param result: 结果
    """
    try:
        _dbMongo[name].insert(dict(itemInfo))
        # print('存储到MongoDB成功')
    except Exception:
        print('存储到MongoDB失败')



def main(shop_urls):
    """
    京东商场评论抓取
    """
    for url in shop_urls:
        browser.get(url)
        text = browser.page_source
        # pattern = 'href="(//item.jd.com/\d+\.html)"'
        # item_url = re.findall(pattern,text)
        item = {}
        html = etree.HTML(text)
        for each in html.xpath('//*[@class="jDesc"]'):
            url = 'https:' + each.xpath('./a/@href')[0]
        # url_list = []
        # for url in item_url:
        #     url = 'https:' + url
        #     if url in url_list:
        #         continue
        #     url_list.append(url)

        # for url in url_list:
            item['url'] = url
            Save_to_mongo('BMWURl',item)

    browser.close()


""" 
程序入口
"""
if __name__ == '__main__':
    # shop_urls = [
    #     'https://bmw.jd.com/view_search-877176-747694-743102-0-2-0-0-1-1-60.html?keyword=%25E6%259C%258D%25E5%258A%25A1&isGlobalSearch=1&other=',
    #     'https://bmw.jd.com/view_search-877176-747694-743102-0-2-0-0-1-2-60.html?keyword=%25E6%259C%258D%25E5%258A%25A1&isGlobalSearch=1&other='
    # ]
    # main(shop_urls)
    df = pd.DataFrame(_dbMongo['BMWURl'].find({}))
    for url in df['url']:
        id = re.search('\d+',url).group()
        _dbRedis.sadd('宝马productID',id)