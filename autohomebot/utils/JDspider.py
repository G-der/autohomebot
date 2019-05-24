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
chrome_options.add_argument('refer=')
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


def CreateProductDetailUrl(key,min_price):
    """ 
    遍历搜索页面
    """
    search_url = _dbRedis.spop(key)
    # browser.maximize_window()
    while search_url:  # 当数据库还存在网页url，取出一个并爬取
        SaveProductDetailUrl(key,search_url,min_price)
        search_url = _dbRedis.spop(key)
        time.sleep(1)


def SaveProductDetailUrl(key,url,min_price):
    """
    保存商品ID
    """
    print(url)
    browser.get(url)
    # 生成移动脚本
    js = "var q=document.documentElement.scrollTop=10000"
    # 执行脚本
    browser.execute_script(js)
    time.sleep(3)

    html = browser.page_source
    # doc = pq(html)
    # items = doc('.gl-item').items()
    doc = etree.HTML(html)
    items = doc.xpath('//*[@class="gl-item"]')
    for item in items:
        price = item.xpath('.//*[@class="p-price"]/strong/i/text()')[0]
        # productID = str(item.find('.p-icons').attr('id')).split('_')[2]
        try:
            if float(price) > min_price:
                productID = item.xpath('./*[@class="gl-i-wrap j-sku-item"]/@data-sku | ./@data-sku')[0]
                print("存入商品ID", productID)
                _dbRedis.sadd("{}productID".format(key), productID)
        except:
            pass


def Get_content(key):
    """
    遍历打开商品页面
    """
    productID = _dbRedis.spop('{}productID'.format(key))
    while productID:  # 当数据库还存在商品id，取出一个并爬取
        productDetailUrl = 'https://item.jd.com/' + quote(productID) + '.html'
        # browser.maximize_window()
        # browser.get(productDetailUrl)

        # crawled_url = _dbMongo[key].find_one({"productDetailUrl": productDetailUrl})
        # if crawled_url:
        #     print(crawled_url["productDetailUrl"], "已抓取")
        #     productID = _dbRedis.spop('{}productID'.format(key))
        #     continue
        get_products(key,productID, productDetailUrl)
        productID = _dbRedis.spop('{}productID'.format(key))
        time.sleep(0.5)


def get_products(key,productID, productDetailUrl):
    """
    提取主要商品数据
    """
    while True:
        try:
            browser.get(productDetailUrl)
        except TimeoutException:
            continue
        print('正在抓取:', productDetailUrl, '的内容')
        break

    html = browser.page_source
    doc = etree.HTML(html)
    itemInfo = ProduceItem()
    # 店铺名
    try:
        shopname = doc.xpath('//*[@class="name"]/a/text() | //*[@class="shopName"]//a/text()')[0] # doc('.shopName').text()
    except:
        shopname = None
    itemInfo['shopname'] = shopname # doc('.name').text()
    # 品牌
    try:
        brand = browser.find_element_by_xpath('//*[@id="parameter-brand"]/li/a').text
    except:
        brand = None
    itemInfo['brand'] = brand  # doc('#parameter-brand li a').text()
    # 商品标题
    try:
        Title = doc.xpath('//*[@class="sku-name"]')
        Title = Title[0].xpath('string(.)').strip()
    except Exception as e:
        print(e)
        Title = None
    itemInfo['productTitle'] = Title # items.find('.sku-name').text()
    # 商品价格
    try:
        price = doc.xpath('//*[@class="p-price"]/span[2]/text()')[0]
    except:
        price = None
    itemInfo['productPrice'] = price  # items.find('.price').text()

    itemInfo['data_from'] = "京东"
    itemInfo['productName'] = key
    itemInfo['productID'] = productID
    itemInfo['productDetailUrl'] = productDetailUrl
    Get_Comment(key,itemInfo)


def Get_Comment(name,itemInfo):
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

    try:
        id = itemInfo['productID']
        # 只看当前商品的时间排序请求
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
            'Referer': 'https://item.jd.com/{}.html'.format(id)
        }
        while True:
            proxies = {'https': 'https://' + str(get_proxie())}
            main_url = "https://club.jd.com/comment/skuProductPageComments.action?productId={}&score=0&sortType=6&page=1&pageSize=10".format(
                id)
            try:
                response = requests.get(main_url,headers=headers)  # ,proxies=proxies
            except:
                continue
            if not response.text:
                print("无返回数据,重试")
                continue
            break
        try:
            data = json.loads(response.text)
        except:
            print("json化失败,url:" + main_url)
            return None
        req = {}
        Summary = data["productCommentSummary"]
        itemInfo["haopingCount"] = Summary["goodCount"]
        itemInfo["zhongpingCount"] = Summary["generalCount"]
        itemInfo["chapingCount"] = Summary["poorCount"]
        itemInfo['allCount'] = Summary["commentCount"]
        if itemInfo["haopingCount"] != 0:
            req["haoping"] = 3
        if itemInfo["zhongpingCount"] != 0:
            req["zhongping"] = 2
        if itemInfo["chapingCount"] != 0:
            req["chaping"] = 1
        if req is {}:
            print("该商品暂无评论")
            return
        for key, value in req.items():
            pg = 0
            max_page = 1  #int(itemInfo[key]) / 10
            retry_count = 1
            while pg < max_page and retry_count < 4:  # 最多只能获取100页数据，最多尝试10次
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
                time_switch = False
                time.sleep(3 * random.uniform(1.5, 2))
                comt_url = "https://club.jd.com/comment/skuProductPageComments.action?productId={}&score={}&sortType=6&page={}&pageSize=10".format(
                    id, value, pg)
                print(itemInfo['productDetailUrl'], key, "第{}页".format(pg))
                # response = get_json(comt_url)
                # proxies = {'https': 'https://' + str(get_proxie())}
                response = requests.get(url=comt_url, headers=headers) #proxies=proxies
                if not response.text:
                    # break
                    if pg < max_page:
                        print("网络错误,重试")
                        time.sleep(10)
                        continue
                    else:
                        print("获取数据失败：", comt_url)
                        break
                try:
                    comt_data = json.loads(response.text)
                except:
                    print("json化失败,url:" + comt_url + response.text)
                    break

                max_page = comt_data["maxPage"]
                if int(max_page) == 0:
                    print("全为默认评论")
                    break

                comments = comt_data["comments"]
                if not comments:
                    print("全为默认评论")
                    break
                for comment in comments:
                    itemInfo['userInfo'] = comment['nickname']
                    itemInfo['orderInfoTime'] = comment['creationTime']
                    # if itemInfo['orderInfoTime'] < START_TIME:
                    #     print("时间截止")
                    #     time_switch = True
                    #     break
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
                    Save_to_mongo(name,itemInfo)
                if time_switch:
                    break
                if len(comments) < 10:
                    print("最后一页")
                    break
                pg += 1

    except Exception as e:
        print("解析出错：", e.__traceback__.tb_lineno, e)


def get_proxie():
    url = 'http://127.0.0.1:5555/random'  # API接口
    # url = 'http://kps.kdlapi.com/api/getkps/?orderid=945555752864198&num=3&pt=1&sep=1'
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

    # # list = ['47.92.126.49:16816', '39.96.209.21:16816', '47.92.129.191:16816']
    # ip = random.choice(list)
    # return ip


# def get_json(url):
#     while True:
#         time.sleep(5)
#         headers = {
#             'User-Agent': random.choice(USER_AGENT_LIST),
#         }
#         proxies = {'https': 'https://' + str(get_proxie())}
#         s = requests.session()
#         s.keep_alive = False  # 关闭多余连接
#         s.headers = headers
#         s.proxies = proxies
#         response = s.get(url)
#         # response = requests.get(url, headers=headers, proxies=proxies)
#         # print(response)
#         if response.status_code == 200 and response.text is not None:
#             return response.text
#         if response.status_code == 404:
#             return None
#         else:
#             print("获取json数据失败,重试")


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
    # start_urls = {
    #     # "前挡玻璃": {"url":"https://list.jd.com/list.html?cat=6728,6742,13246&ev=4722_84603&page={}&sort=sort_commentcount_desc&trans=1&JL=6_0_0#J_main","maxpge":23,"minprice":300},
    #     # "后挡玻璃": {"url":"https://list.jd.com/list.html?cat=6728,6742,13246&ev=4722_84605&page={}&sort=sort_commentcount_desc&trans=1&JL=2_1_0#J_crumbsBar","maxpge":2,"minprice":300},
    #     # "侧窗玻璃": {"url":"https://list.jd.com/list.html?cat=6728,6742,13246&ev=4722_84604&page={}&sort=sort_commentcount_desc&trans=1&JL=2_1_0#J_crumbsBar","maxpge":2,"minprice":300},
    #     # "保险前杆": {"url":"https://search.jd.com/search?keyword=%E4%BF%9D%E9%99%A9%E6%9D%A0&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&suggest=2.his.0.0&psort=4&cid2=6745&cid3=14905&ev=8164_96716%5E&page={}&s=1&click=0","maxpge":43,"minprice":200},
    #     # "保险后杆": {"url":"https://search.jd.com/search?keyword=%E4%BF%9D%E9%99%A9%E6%9D%A0&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&suggest=2.his.0.0&psort=4&cid2=6745&cid3=14905&ev=8164_96715%5E&page={}&s=541&click=0","maxpge":19,"minprice":200},
    #     # "保险侧杆": {"url":"https://search.jd.com/search?keyword=%E4%BF%9D%E9%99%A9%E6%9D%A0&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&suggest=2.his.0.0&psort=4&cid2=6745&cid3=14905&ev=8164_108805%5E&page={}&s=841&click=0","maxpge":29,"minprice":200},
    #     "正时皮带": {"url":"https://list.jd.com/list.html?cat=6728,6742,13244&ev=exbrand_12020%7C%7C27213%7C%7C6927%7C%7C51288%7C%7C61546%7C%7C55775%7C%7C3623%7C%7C51286%7C%7C51290%7C%7C64095%7C%7C252644%7C%7C18177%7C%7C288885%7C%7C4754%7C%7C159529%7C%7C177986%7C%7C64109%7C%7C230847&page={}","maxpge":127,"minprice":0}
    # }
    # 创建URL
    # for pageInx in range(1, MAX_PAGE + 1):
    #     # 京东的分布增长为1,3,5,6
    #     # pageInx = 2 * pageInx - 1
    #     # 创建url
    #     CreateSearchUrl(pageInx)

    # 所有商品详细内容URL
    # for key,item in start_urls.items():
        # url = start_urls[key]["url"]
        # max_page = start_urls[key]["maxpge"]
        # min_price = start_urls[key]["minprice"]
        # # CreateSearchUrl(key,url,max_page)
        # CreateProductDetailUrl(key,min_price)

        # 抓取界面内容
        # Get_content(key)
    key = "沙拉酱"
    Get_content(key)
    browser.close()


""" 
程序入口
"""
if __name__ == '__main__':
    # 添加key
    key = '沙拉酱'
    # ids = ['29972792492','31638226145','1303111']
    ids = ['2047135','838548','838553','4876235',
           '10432822549','11051017630','10433102772',
           '11814414099','25693483918','11070694564',
           '26179155541','25747412220','12859474237',
           '31950933332','25872643279','11814766424',
           '29079886891','13416617294']
    for id in ids:
        _dbRedis.sadd("{}productID".format(key), id)
    main()
