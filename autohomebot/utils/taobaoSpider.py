# coding=utf-8
import json
import math
import random
import re
import time
import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
import redis
import pymongo
from lxml import etree
from items import ProduceItem
from dateutil.parser import parse

MONGO_URL = 'absit1309'
MONGO_DB = 'taobao'
MONGO_COLLECTION = '沙拉酱'
START_TIME = "2018-01-01"
MAX_PAGE = 100
KEYWORD = '沙拉酱'
PROGRAME_STARTTIME = parse(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

# MongoDB抓取结果存储数据库
_client = pymongo.MongoClient(MONGO_URL)
_dbMongo = _client[MONGO_DB]

# RedisDB抓取URLS存储数据库
redisPool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True, db=1)
_dbRedis = redis.Redis(connection_pool=redisPool)

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 禁止图片加载
browser = webdriver.Chrome(chrome_options=chrome_options)
browser.implicitly_wait(15)


def CreateSearchUrl(page):
    """
    创建URL
    :param keyword:页数
    """
    try:
        searchUrl = "https://s.taobao.com/search?ie=utf8&initiative_id=staobaoz_20190401&stats_click=search_radio_all%3A1&js=1&imgfile=&q=%E6%9C%BA%E6%B2%B9&suggest=history_1&_input_charset=utf-8&wq=&suggest_query=&source=suggest&cps=yes&ppath=20000%3A133794%3B20000%3A133795%3B20000%3A133796&s={}".format(
            page)
        print('以关键字所查询的结果的前{}页商品的URLS:'.format(MAX_PAGE), searchUrl)
        _dbRedis.sadd("TBsearchResultUrls", searchUrl)
    except TimeoutException:
        CreateSearchUrl(page)


def CreateProductDetailUrl():
    """
    遍历搜索页面
    """
    search_url = _dbRedis.spop('TBsearchResultUrls')
    browser.maximize_window()
    while search_url:  # 当数据库还存在网页url，取出一个并爬取
        SaveProductDetailUrl(search_url)
        search_url = _dbRedis.spop('TBsearchResultUrls')
        time.sleep(0.5)


def SaveProductDetailUrl(url):
    """
    保存商品链接
    """
    browser.get(url)
    browser.implicitly_wait(10)
    # 登录淘宝
    while True:
        if "手机扫码，安全登录" in browser.page_source:
            print("请扫码登录")
            time.sleep(30)
            continue
        if "二维码失效" in browser.page_source:
            print("二维码失效，刷新")
            browser.find_element_by_xpath('//a[contains(text(),"请点击刷新")]').click()
            time.sleep(30)
            continue
        break
    # 生成移动脚本
    js = "var q=document.documentElement.scrollTop=10000"
    # 执行脚本
    browser.execute_script(js)
    # 等待页面加载
    time.sleep(3)
    # 隐式等待元素加载
    browser.implicitly_wait(10)

    html = browser.page_source
    doc = etree.HTML(html)
    items = doc.xpath('//div[@class="item J_MouserOnverReq  "]')
    for item in items:
        product_url = item.xpath('.//div[@class="row row-2 title"]/a/@href')[0]
        productDetailUrl = 'https://' + product_url
        print('正在生成各商品详细信息的URLS:', productDetailUrl)
        _dbRedis.sadd("TBproductDetailUrls", productDetailUrl)


def Get_content():
    # url = _dbRedis.spop("TBproductDetailUrls")
    # url = 'https://item.taobao.com/item.htm?spm=a230r.1.14.72.701d7285KfyCz3&id=585485599973&ns=1&abbucket=6#detail '
    url = 'https://detail.tmall.com/item.htm?spm=a230r.1.14.1.3f195228YlslIJ&id=40880131694&ns=1&abbucket=17'
    while url:
        parse_main(url)
        # url = _dbRedis.spop("TBproductDetailUrls")
        time.sleep(1)


def parse_main(url):
    print("正在抓取", url, "的数据")
    try:
        browser.get(url)
        while True:
            try:

                break
            except TimeoutException:
                print("获取网页超时，刷新重试")
                browser.refresh()
        time.sleep(3)
        # try:
        #     close = browser.find_elements_by_id("sufei-dialog-close")[0]
        #     if close:
        #         browser.execute_script("arguments[0].click()", close)
        #         browser.implicitly_wait(10)
        #         time.sleep(3)
        # except:
        #     pass
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
            title_path = doc.xpath('//h3[@class="tb-main-title"]/@data-title')[0]
            if not title_path:
                title_path = doc.xpath('//div[@class="tb-detail-hd"]//h1/text()')[0]
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
        item['productName'] = KEYWORD
        item['productDetailUrl'] = browser.current_url
        item['productID'] = re.search(r'id=(\d+)', browser.current_url).group(1)
        Get_Comment(item)
    except Exception as e:
        print(e.__traceback__.tb_lineno,e)


def Get_Comment(item):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        # TODO添加cookie
        'cookie': 't=b3ce8ce30e0f952b1e3b14b5e2c71e56; cna=MRoWFfF9mGUCAXkPpllRTWCS; thw=cn; cookie2=1e8bd90e67601b5b7f32c4a8c03c8150; _tb_token_=e713855e53806; uc3=vt3=F8dByEnb20FJxi8z0BU%3D&id2=W80oUssVPE7u&nk2=Gh6OGoNE19F4u6HIo8GE&lg2=UtASsssmOIJ0bQ%3D%3D; tracknick=yuzhongde125049; lgc=yuzhongde125049; _cc_=U%2BGCWk%2F7og%3D%3D; tg=0; enc=NgQXFBTXh1qRL10IlnNnyPTopRowvkLhgagbAyTlDCu135zh7asTLq3yrXQlImUJUOcPJB9RovNnCkXGKXB1VQ%3D%3D; hng=CN%7Czh-CN%7CCNY%7C156; swfstore=263282; alitrackid=www.taobao.com; lastalitrackid=www.taobao.com; mt=ci=0_1; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0%26__ll%3D-1%26_ato%3D0; UM_distinctid=169dd28a8ec45c-0dd9c4a72b6f1e-5f1d3a17-100200-169dd28a8ed39f; whl=-1%260%260%261554195183110; JSESSIONID=994DB56D701AC23E7929BDC6B547A2B4; v=0; _m_h5_tk=c442659108b1406453c44c336f685645_1554268583064; _m_h5_tk_enc=a51a766918d65c0cbef1007751a824e1; uc1=cookie14=UoTZ4M309yR%2Ffg%3D%3D; l=bBaGIq-HvpjdtafSBOfNGZO8E5_OFQAfGsPPhzt6pICPOeXCP2ERWZsJ8et6C3GVa6fJR3-Uun2LBALZ4y4Eh; isg=BJqaIX51kjGazx6tcVpBjCND60C2Z_y6A9NCcqQRaSz_Fz9RjFiJtCAl56Mux5Y9'
    }
    try:
        id = item['productID']
        # 商品评论
        main_url = "https://rate.taobao.com/detailCommon.htm?auctionNumId={}".format(
            id)
        try:
            response = requests.get(main_url, headers=headers, timeout=1, allow_redirects=False)
        except Exception as e:
            print("请求评论数错误:", e)
        if response.status_code != 200:
            print("请求评论数错误:",response.status_code)
        dic = re.search(r'\((.*)\)', response.text).group(1)
        data = json.loads(dic)
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
            max_page = 1
            while pg <= max_page:
                now = parse(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                # if now.hour == 1:
                #     print("凌晨一点,爬虫休眠")
                #     time.sleep(60*60*6)
                # global PROGRAME_STARTTIME
                # if (now-PROGRAME_STARTTIME).seconds >= 3600:
                #     print("连续抓取一小时，休息20分钟")
                #     time.sleep(20*60)
                #     PROGRAME_STARTTIME = parse(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                time_switch = False
                time.sleep(1)
                comt_url = "https://rate.taobao.com/feedRateList.htm?auctionNumId={}&currentPageNum={}&pageSize=20&rateType={}&orderType=feedbackdate&folded=0".format(
                    id, pg, value)
                print(item['productDetailUrl'], key, "第{}页".format(pg))
                try:
                    response = requests.get(comt_url, headers=headers, timeout=1, allow_redirects=False)
                except Exception as e:
                    print("请求评论详情错误:", e)
                if response.status_code != 200:
                    print("请求评论详情错误:", response.status_code, "更新登录信息")
                    return None
                if not response.text:
                    print("获取数据失败，重试")
                    time.sleep(60)
                    continue
                # print(response.text)
                dic = re.search(r'\((.*)\)', response.text).group(1)
                data = json.loads(dic)
                total = data["total"]
                if total == 0:
                    print("无详细评价")
                    break
                max_page = math.ceil(total / 20)
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
                    Save_to_mongo(item)
                if time_switch:
                    break
                pg += 1
    except Exception as e:
        print("解析出错：", e.__traceback__.tb_lineno, e)


def Save_to_mongo(item):
    """
    保存至MongoDB
    :param result: 结果
    """
    try:
        _dbMongo[MONGO_COLLECTION].insert(dict(item))
        # print('存储到MongoDB成功')
    except Exception:
        print('存储到MongoDB失败')


def main():
    """
    淘宝评论抓取
    """
    # # 创建URL
    # for pageInx in range(1, MAX_PAGE + 1):
    #     # 淘宝的分布增长为0，44，88，132
    #     pageInx = 44 * (pageInx - 1)
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
