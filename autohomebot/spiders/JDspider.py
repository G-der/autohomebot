# coding=utf-8
import json
import random
import time
from urllib.parse import quote
import pymongo
import redis
from pyquery import PyQuery as pq
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from autohomebot.items import ProduceItem
import requests

# import sys
# sys.setrecursionlimit(100000)

MONGO_URL = 'localhost'
MONGO_DB = 'jingdong'
MONGO_COLLECTION = '京东products'
BRAND = "&ev=exbrand_美孚（Mobil）%7C%7C壳牌（Shell）%7C%7C嘉实多（Castrol）%5E"
START_TIME = "2018-01-01"
KEYWORD = '机油'
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
chrome_options.add_argument('--ignore-certificate-errors')
browser = webdriver.Chrome(chrome_options=chrome_options,
                           # executable_path=path_to_chromedriver
                           )


def CreateSearchUrl(page):
    """ 
    创建URL
    :param keyword:页数
    """
    try:
        searchUrl = "https://list.jd.com/list.html?cat=6728,6742,11849&ev=878_69855%7C%7C69856%7C%7C105097%7C%7C76142%7C%7C87652%7C%7C103220%7C%7C33710%40exbrand_12400%7C%7C10476%7C%7C9074%7C%7C6927%7C%7C51288%7C%7C61546%7C%7C55775%7C%7C3623%7C%7C51286%7C%7C51290%7C%7C64095%7C%7C252644%7C%7C18177%7C%7C288885%7C%7C4754%7C%7C159529%7C%7C177986%7C%7C64109%7C%7C230836&page={}&sort=sort_totalsales15_desc&trans=1&JL=6_0_0#J_main".format(
            page)
        # searchUrl = 'https://search.jd.com/Search?keyword=' + quote(KEYWORD) + '&enc=utf-8' + '&page=' + quote(str(page)) + BRAND
        print('以关键字所查询的结果的前{}页商品的URLS:'.format(MAX_PAGE), searchUrl)
        _dbRedis.sadd("searchResultUrls", searchUrl)
    except TimeoutException:
        CreateSearchUrl(page)


def CreateProductDetailUrl():
    """ 
    遍历搜索页面
    """
    search_url = _dbRedis.spop('searchResultUrls')
    # browser.maximize_window()
    while search_url:  # 当数据库还存在网页url，取出一个并爬取
        SaveProductDetailUrl(search_url)
        search_url = _dbRedis.spop('searchResultUrls')
        time.sleep(0.5)


def SaveProductDetailUrl(url):
    """
    保存商品ID
    """
    browser.get(url)
    browser.implicitly_wait(10)
    # 生成移动脚本
    js = "var q=document.documentElement.scrollTop=10000"
    # 执行脚本
    browser.execute_script(js)
    # 隐式等待元素加载
    browser.implicitly_wait(10)

    html = browser.page_source
    doc = pq(html)
    items = doc('.gl-item').items()
    for item in items:
        # productID = str(item.find('.p-icons').attr('id')).split('_')[2]
        productID = str(item.find('.gl-i-wrap.j-sku-item').attr('data-sku'))
        # productDetailUrl = 'https://item.jd.com/' + quote(productID) + '.html'
        # print('正在生成各商品详细信息的URLS:', productDetailUrl)
        # _dbRedis.sadd("productDetailUrls", productDetailUrl)
        print("存入商品ID", productID)
        _dbRedis.sadd("productID", productID)


def Get_content():
    """
    遍历打开商品页面
    """
    productID = _dbRedis.spop('productID')
    while productID:  # 当数据库还存在商品id，取出一个并爬取
        productDetailUrl = 'https://item.jd.com/' + quote(productID) + '.html'
        browser.maximize_window()
        browser.get(productDetailUrl)
        print('正在抓取:', productDetailUrl, '的内容')
        get_products(productID, productDetailUrl)
        productID = _dbRedis.spop('productID')
        time.sleep(0.5)


def get_products(productID, productDetailUrl):
    """
    提取主要商品数据
    """
    browser.get(productDetailUrl)
    html = browser.page_source
    doc = pq(html)
    itemInfo = ProduceItem()
    itemInfo['shopname'] = doc('.name').text()
    itemInfo['brand'] = None  # doc('#parameter-brand li a').text()
    try:
        brand = browser.find_element_by_xpath('//*[@id="parameter-brand"]/li/a')
        itemInfo['brand'] = brand.text
    except:
        print("无品牌信息")

    itemInfo['data_from'] = "京东"
    itemInfo['productName'] = KEYWORD
    if not itemInfo['shopname']:
        itemInfo['shopname'] = doc('.shopName').text()
    # for item in items:
    items = doc('.itemInfo-wrap')
    itemInfo['productTitle'] = items.find('.sku-name').text()
    itemInfo['productPrice'] = items.find('.price').text()
    itemInfo['productID'] = productID
    itemInfo['productDetailUrl'] = productDetailUrl
    Get_Comment(itemInfo)


def Get_Comment(itemInfo):
    """ 
    提取当前商品的评价
    """
    # js = "var q=document.documentElement.scrollTop=10000"
    # browser.execute_script(js)
    # browser.implicitly_wait(10)
    # # 选择商品评价
    # browser.find_element_by_xpath('//li[@data-anchor="#comment"]').click()
    #
    # # 窗体下拉,进行界面刷新
    # js = "var q=document.documentElement.scrollTop=10000"
    # browser.execute_script(js)
    # # 隐式等待元素加载
    # browser.implicitly_wait(10)
    #
    # html = browser.page_source
    # doc = pq(html)
    # items = doc('.comment-item').items()
    # for item in items:
    #     itemInfo['orderInfoTitle'] = item.find('.user-info').text()
    #
    #     temp=item.find('.order-info').text()
    #     itemInfo['orderInfoTime'] = temp.split('\n')[len(temp.split('\n'))-1]
    #     itemInfo['orderInfoTitle'] = temp.replace(itemInfo['orderInfoTime'], '')
    #
    #     itemInfo['comment_con'] = item.find('.comment-con').text()
    #
    #     #保存主体信息
    #     Save_to_mongo(itemInfo)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }
    try:
        id = itemInfo['productID']
        # 只看当前商品的时间排序请求
        main_url = "https://club.jd.com/comment/skuProductPageComments.action?productId={}&score=0&sortType=6&page=1&pageSize=10".format(
            id)
        response = requests.get(url=main_url, headers=headers)
        if not response.text:
            print("获取json数据失败")
        try:
            data = json.loads(response.text)
        except:
            print("json化失败,url:" + main_url)

        req = {}
        Summary = data["productCommentSummary"]
        itemInfo["haopingCount"] = Summary["goodCount"]
        itemInfo["zhongpingCount"] = Summary["generalCount"]
        itemInfo["chapingCount"] = Summary["poorCount"]
        if itemInfo["haopingCount"] != 0:
            req["haopingCount"] = 3
        if itemInfo["zhongpingCount"] != 0:
            req["zhongpingCount"] = 2
        if itemInfo["chapingCount"] != 0:
            req["chapingCount"] = 1
        if req is {}:
            return
        for key, value in req.items():
            pg = 1
            max_page = int(itemInfo[key]) / 10
            if max_page > 100:
                max_page = 100
            while pg <= max_page:  # 最多只能获取100页数据
                # maxPage = browser.find_element_by_xpath('')
                # scroll_add_crowd_button = browser.find_element_by_xpath('//*[@id="askAnswer"]/div[1]')
                # browser.execute_script("arguments[0].scrollIntoView();", scroll_add_crowd_button)
                # js = "var q=document.documentElement.scrollTop=10000"
                # browser.execute_script(js)
                # # 隐式等待元素加载
                # browser.implicitly_wait(10)
                #
                # browser.find_element_by_xpath('//a[@clstag="shangpin|keycount|product|pinglunfanye-nextpage"]').click()
                #
                # js = "var q=document.documentElement.scrollTop=10000"
                # browser.execute_script(js)
                # # 隐式等待元素加载
                # browser.implicitly_wait(10)
                #
                # html = browser.page_source
                # doc = pq(html)
                # items = doc('.comment-item').items()
                # for item in items:
                #     itemInfo['orderInfoTitle'] = item.find('.user-info').text()
                #
                #     temp=item.find('.order-info').text()
                #     itemInfo['orderInfoTime'] = temp.split('\n')[len(temp.split('\n'))-1]
                #     itemInfo['orderInfoTitle'] = temp.replace(itemInfo['orderInfoTime'], '')
                #
                #     itemInfo['comment_con'] = item.find('.comment-con').text()
                #
                #     #保存主体信息
                time_swich = 0
                time.sleep(3 * random.uniform(1.5, 2))
                comt_url = "https://club.jd.com/comment/skuProductPageComments.action?productId={}&score={}&sortType=6&page={}&pageSize=10".format(
                    id, value, pg)
                print(itemInfo['productDetailUrl'], key, itemInfo[key], "第{}页".format(pg))
                response = requests.get(url=comt_url, headers=headers)
                if not response.text:

                    if pg < max_page:
                        print("被反，休眠")
                        time.sleep(5 * 60)
                        continue
                    else:
                        print("获取数据失败：", comt_url)
                        break
                try:
                    comt_data = json.loads(response.text)
                except:
                    print("json化失败,url:" + main_url)
                    break
                comments = comt_data["comments"]
                if not comments:
                    print("数据获取完成")
                    break
                for comment in comments:
                    itemInfo['userInfo'] = comment['nickname']
                    itemInfo['orderInfoTime'] = comment['creationTime']
                    if itemInfo['orderInfoTime'] < START_TIME:
                        print("时间截止")
                        time_swich = 1
                        break
                    itemInfo['orderInfoTitle'] = comment['referenceName']
                    itemInfo['comment_con'] = comment['content']
                    score = int(comment['score'])
                    if score in range(1, 3):
                        itemInfo['comment_type'] = "差评"
                    elif score == 3:
                        itemInfo['comment_type'] = "中评"
                    else:
                        itemInfo['comment_type'] = "好评"
                    itemInfo["catch_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    Save_to_mongo(itemInfo)
                if time_swich == 1:
                    break
                pg += 1

    except Exception as e:
        print("获取json数据出错：", e.__traceback__.tb_lineno, e)


def Save_to_mongo(itemInfo):
    """
    保存至MongoDB
    :param result: 结果
    """
    try:
        _dbMongo[MONGO_COLLECTION].insert(dict(itemInfo))
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
    # 创建URL
    # for pageInx in range(1, MAX_PAGE + 1):
    #     # 京东的分布增长为1,3,5,6
    #     # pageInx = 2 * pageInx - 1
    #     # 创建url
    #     CreateSearchUrl(pageInx)
    #
    # # 所有商品详细内容URL
    # CreateProductDetailUrl()

    # 抓取界面内容
    Get_content()

    browser.close()


""" 
程序入口
"""
if __name__ == '__main__':
    main()
