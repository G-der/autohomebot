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


""" 
程序主体
"""


def main():
    """
    京东商场评论抓取
    """
    data = pd.read_excel(r'C:\Users\apeng\Desktop\nanshopurl.xlsx')
    urls = data['sonbbs_name']
    itemInfo = {}
    for url in urls:
        browser.get(url)
        html = browser.page_source
        doc = etree.HTML(html)
        # 店铺名
        try:
            shopname = doc.xpath('//*[@class="name"]/a/text() | //*[@class="shopName"]//a/text()')[0]  # doc('.shopName').text()
        except:
            shopname = None
        itemInfo['shopname'] = shopname  # doc('.name').text()
        itemInfo['url'] = url
        Save_to_mongo("JDSHOP2",itemInfo)
    browser.close()


""" 
程序入口
"""
if __name__ == '__main__':
    main()
