#coding:utf-8
import re
import time
from selenium import webdriver
import redis
import pymongo
from lxml import etree

MONGO_URL = 'absit1309'
MONGO_DB = 'weibo'
# MongoDB抓取结果存储数据库
_client = pymongo.MongoClient(MONGO_URL)
_dbMongo = _client[MONGO_DB]

# redis设置
pool = redis.ConnectionPool(host = "localhost",port="6379",decode_responses=True)
_redisdb = redis.Redis(connection_pool=pool)

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--ignore-certificate-errors')
# chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 禁止图片加载
browser = webdriver.Chrome(chrome_options=chrome_options)
browser.implicitly_wait(10)

def time_change(pushtime):
    # print(time.strftime("%Y-%m-%d", time.localtime(time.time())))
    pushtime = str(pushtime)
    if re.search("昨天", pushtime):
        yestoday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 86400))
        pushtime = yestoday
    if re.search('前天', pushtime):
        Byestoday = time.strftime("%Y-%m-%d", time.localtime(time.time() - 172800))
        pushtime = Byestoday
    if re.search('今天|小时前|分钟前', pushtime):
        today = time.strftime("%Y-%m-%d", time.localtime(time.time()))
        pushtime = today
    # if re.search('小时前', pushtime):
    #     NUM = int(re.search('\d+', pushtime).group())
    #     sec = NUM * 60 * 60
    #     today = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time() - sec))
    #     pushtime = today
    # if re.search('分钟前', pushtime):
    #     NUM = int(re.search('\d+', pushtime).group())
    #     sec = NUM * 60
    #     today = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time() - sec))
    #     pushtime = today
    return pushtime

def get_url(key):
    # 生成移动脚本
    js = "var q=document.documentElement.scrollTop=10000"
    # 执行脚本
    browser.execute_script(js)
    # 等待页面加载
    time.sleep(3)
    text = browser.page_source
    html = etree.HTML(text)
    pattern = '<.*?href="(//weibo.com/\d+/.*?\?refer_flag=.*?)".*?>'
    link_list = re.findall(pattern=pattern,string=text)
    # print(link_list)
    for url in link_list:
        url = 'https:'+ url
        _redisdb.sadd(key,url)
    next_page = html.xpath('//div[@class="m-page"]/div/a[last()]')[0]
    if next_page.xpath('./text()')[0] == '下一页':
        next_url = 'https://s.weibo.com' + next_page.xpath('./@href')[0]
        index = int(re.search(r'&page=(\d+)',next_url).group(1))
        if index < 51:
            browser.get(next_url)
            get_url()


def get_main(key):
    url = _redisdb.spop('key')
    # url = 'https://weibo.com/3124358693/HuE046k4a?refer_flag=1001030103_'
    while url:
        browser.get(url)
        while True:
            js = "var q=document.documentElement.scrollTop=10000"
            # 执行脚本
            browser.execute_script(js)
            time.sleep(1.5)
            try:
                more = browser.find_element_by_xpath('//a[@action-type="click_more_comment"]')
                more.click()
            except:
                break
        doc = browser.page_source
        html = etree.HTML(doc)
        item = {}
        try:
            main_text_path = html.xpath('//div[@node-type="feed_list_content"]')[0]
            main_text = main_text_path.xpath('string(.)').strip()
        except Exception as e:
            print(e.__traceback__.tb_lineno,e)
            main_text = None
        item['main_text'] = main_text
        comment_list = html.xpath('//*[@class="list_li S_line1 clearfix"]')
        for i in comment_list:
            comment_path = i.xpath('.//*[@class="WB_text"]')[0]
            user_name = comment_path.xpath('./a[1]/text()')[0]
            comment_detail = comment_path.xpath('./text()[2]')[0]
            push_time = i.xpath('.//*[@class="WB_from S_txt2"]/text()')[0]
            if not re.search('年',push_time):
                push_time = '2019年' + push_time
            push_time = time_change(push_time)
            push_time = push_time.replace('年','-').replace('月','-').replace('日','')
            item['user_name'] = user_name
            item['comment_detail'] = comment_detail
            item['push_time'] = push_time
            Save_to_mongo(key,item)
        # url = _redisdb.spop('weibourl')

def Save_to_mongo(name,itemInfo):
    try:
        _dbMongo[name].insert(dict(itemInfo))
    except Exception:
        print('存储到MongoDB失败')


def main():
    kw = "自动驾驶"
    url = 'https://s.weibo.com/weibo?q={}&Refer=index'.format(kw)
    browser.get(url)
    print('等待登陆')
    time.sleep(60)
    get_url(kw)
    get_main(kw)


if __name__ == '__main__':
    main()

