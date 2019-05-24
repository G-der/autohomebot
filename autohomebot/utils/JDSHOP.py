# coding=utf-8
import json
import random
import re
import time
from urllib.parse import quote
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



USER_AGENT_LIST = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
        "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
        "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/2.0 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.71 Safari/537.1 LBBROWSER",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; LBBROWSER)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E; LBBROWSER)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.84 Safari/535.11 LBBROWSER",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E; QQBrowser/7.0.3698.400)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SV1; QQDownload 732; .NET4.0C; .NET4.0E; 360SE)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; QQDownload 732; .NET4.0C; .NET4.0E)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1",
        "Mozilla/5.0 (iPad; U; CPU OS 4_2_1 like Mac OS X; zh-cn) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b13pre) Gecko/20110307 Firefox/4.0b13pre",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Mozilla/5.0 (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10"
    ]
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
# browser.get("https://www.jd.com")
# time.sleep(70)

def CreateSearchUrl(key,url,page):
    """ 
    创建URL
    :param keyword:页数
    """
    print('以关键字所查询的结果的前{}页商品的URLS:'.format(page))
    try:
        for i in range(1,page):
            searchUrl = url.format(i)
            _dbRedis.sadd(key, searchUrl)
    except TimeoutException:
        CreateSearchUrl(key,url,page)


def CreateProductDetailUrl(key):
    """ 
    遍历搜索页面
    """
    search_url = _dbRedis.spop(key)
    # browser.maximize_window()
    while search_url:  # 当数据库还存在网页url，取出一个并爬取
        SaveProductDetailUrl(search_url)
        search_url = _dbRedis.spop(key)
        time.sleep(1)


def SaveProductDetailUrl(url):
    """
    保存店铺名
    """
    print(url)
    browser.get(url)
    # 生成移动脚本
    js = "var q=document.documentElement.scrollTop=10000"
    # 执行脚本
    browser.execute_script(js)
    time.sleep(3)

    html = browser.page_source
    doc = etree.HTML(html)
    items = doc.xpath('//*[@class="gl-item"]')
    dic = {}
    for item in items:
        # price = item.xpath('.//*[@class="p-price"]/strong/i/text()')[0]
        # productID = str(item.find('.p-icons').attr('id')).split('_')[2]
        try:
            url = "https:" + item.xpath('.//*[starts-with(@class,"p-name")]/a/@href')[0]
            shopname = item.xpath('.//*[@class="p-shop"]//a/@title')
            if shopname:
                dic['shopname'] = shopname[0]
            else:
                dic['shopname'] = '自营'
            dic['url'] = url

            Save_to_mongo("JDSHOP",dic)
        except Exception as e:
            print(url,e.__traceback__.tb_lineno,e)



def get_proxie():
    # url = 'http://127.0.0.1:5555/random'  # API接口
    url = 'http://kps.kdlapi.com/api/getkps/?orderid=945555752864198&num=3&pt=1&sep=1'
    while True:
        try:
            r = requests.get(url, timeout=8)
            break
        except:
            continue
    if r.status_code == 200:
        text = r.text
        ips = re.findall(r'\d+.\d+.\d+.\d+:\d+',text)
        if ips == None:
            time.sleep(1)
            return get_proxie()
        else:
            ip = random.choice(ips)
            return ip
    else:
        time.sleep(1)
        return get_proxie()



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
    start_urls = {
        "机油": {"url":"https://list.jd.com/list.html?cat=6728,6742,11849&ev=878_69855%7C%7C69856%7C%7C105097%7C%7C76142%7C%7C87652%7C%7C103220%7C%7C33710%40exbrand_12400%7C%7C10476%7C%7C9074%7C%7C6927%7C%7C51288%7C%7C61546%7C%7C55775%7C%7C3623%7C%7C51286%7C%7C51290%7C%7C64095%7C%7C252644%7C%7C18177%7C%7C288885%7C%7C4754%7C%7C159529%7C%7C177986%7C%7C64109%7C%7C230836&sort=sort_totalsales15_desc&trans=1&JL=3_%E5%93%81%E7%89%8C_%E7%BE%8E%E5%AD%9A%EF%BC%88Mobil%EF%BC%89#J_crumbsBar&page={}","maxpge":100},
        "机率": {"url":"https://list.jd.com/list.html?cat=6728,6742,11852&ev=exbrand_12014%7C%7C5125%7C%7C12267%7C%7C6927%7C%7C51288%7C%7C61546%7C%7C55775%7C%7C3623%7C%7C51286%7C%7C51290%7C%7C64095%7C%7C252644%7C%7C18177%7C%7C288885%7C%7C4754%7C%7C159529%7C%7C177986%7C%7C64109%7C%7C230836&page={}","maxpge":238},
        "雨刷": {"url":"https://list.jd.com/list.html?cat=6728,6742,6766&ev=exbrand_5125%7C%7C9987%7C%7C32%7C%7C6927%7C%7C51288%7C%7C61546%7C%7C55775%7C%7C3623%7C%7C51286%7C%7C51290%7C%7C64095%7C%7C252644%7C%7C18177%7C%7C288885%7C%7C4754%7C%7C159529%7C%7C177986%7C%7C64109%7C%7C230836&page={}","maxpge":55},
        "轮胎": {"url": "https://list.jd.com/list.html?cat=6728,6742,9248&ev=exbrand_12836%7C%7C14071%7C%7C165779%7C%7C6927%7C%7C51288%7C%7C61546%7C%7C55775%7C%7C3623%7C%7C51286%7C%7C51290%7C%7C64095%7C%7C252644%7C%7C18177%7C%7C288885%7C%7C4754%7C%7C159529%7C%7C177986%7C%7C64109%7C%7C230838&page={}","maxpge": 91},
        "刹车油": {"url":"https://list.jd.com/list.html?cat=6728,6742,14880&ev=exbrand_5125%7C%7C48928%7C%7C6816%7C%7C6927%7C%7C51288%7C%7C61546%7C%7C55775%7C%7C3623%7C%7C51286%7C%7C51290%7C%7C64095%7C%7C252644%7C%7C18177%7C%7C288885%7C%7C4754%7C%7C159529%7C%7C177986%7C%7C64109%7C%7C230840&page={}","maxpge":196},
        "刹车盘": {"url":"https://list.jd.com/list.html?cat=6728,6742,14879&ev=exbrand_6816%7C%7C2591%7C%7C44958%7C%7C260643%7C%7C6927%7C%7C51288%7C%7C61546%7C%7C55775%7C%7C3623%7C%7C51286%7C%7C51290%7C%7C64095%7C%7C252644%7C%7C18177%7C%7C288885%7C%7C4754%7C%7C159529%7C%7C177986%7C%7C64109%7C%7C230842&page={}","maxpge":74},
        "刹车片": {"url":"https://list.jd.com/list.html?cat=6728,6742,11859&ev=exbrand_5125%7C%7C6816%7C%7C2591%7C%7C6927%7C%7C51288%7C%7C61546%7C%7C55775%7C%7C3623%7C%7C51286%7C%7C51290%7C%7C64095%7C%7C252644%7C%7C18177%7C%7C288885%7C%7C4754%7C%7C159529%7C%7C177986%7C%7C64109%7C%7C230844&page={}","maxpge":100},
        "正时皮带": {"url":"https://list.jd.com/list.html?cat=6728,6742,13244&ev=exbrand_12020%7C%7C27213%7C%7C6927%7C%7C51288%7C%7C61546%7C%7C55775%7C%7C3623%7C%7C51286%7C%7C51290%7C%7C64095%7C%7C252644%7C%7C18177%7C%7C288885%7C%7C4754%7C%7C159529%7C%7C177986%7C%7C64109%7C%7C230847&page={}","maxpge":133}
    }

    # 所有商品详细内容URL
    for key,item in start_urls.items():
        url = start_urls[key]["url"]
        max_page = start_urls[key]["maxpge"]
        # min_price = start_urls[key]["minprice"]
        # CreateSearchUrl(key,url,max_page)
        CreateProductDetailUrl(key)


    browser.close()


""" 
程序入口
"""
if __name__ == '__main__':
    main()
