#!/usr/bin/env python 3
# encoding: utf-8
from time import time
import pymongo
import requests
from lxml import etree
import re
import random
import time
from pymongo import MongoClient
from urllib import parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--proxy-server=10.172.226.35:8080')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
# chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 禁止图片加载
browser = webdriver.Chrome(chrome_options=chrome_options)

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
random_ua = ''
proxy = None
START_TIME = "2017-01-01"


def get_randon_ua():
    random_ua = random.choice(USER_AGENT_LIST)
    return random_ua


def get_proxie():
    url = 'http://127.0.0.1:5555/random'  # API接口
    r = requests.get(url, timeout=8)
    if r.status_code == 200:
        ip = r.text
        if ip == None:
            time.sleep(1)
            return get_proxie()
        else:
            return ip
    else:
        time.sleep(1)
        return get_proxie()


def get_url_list(list_url, headers, proxy):
    if proxy:
        try:
            art_list_url = []
            art_list = requests.get(list_url, headers=headers, timeout=8, proxies=proxy)
            if '回答' in str(art_list.text):  # 设置标志性文本防止被重定向
                print('解析成功，正在获取帖子链接', list_url)
                html = etree.HTML(art_list.text)
                item_path = html.xpath("//*[@class='list-dl']")
                for item in item_path:
                    art_url = item.xpath('.//a/@href')[0]
                    if "autohome" not in art_url:
                        continue
                    else:
                        # topic_url = 'https:' + item
                        art_list_url.append(art_url)
                next_path = html.xpath('.//a[@class="page-item-next"]/@href')
                if next_path != []:
                    next_url = 'https://sou.autohome.com.cn/zhidao' + next_path[0]
                    return {"art_list_url": art_list_url,
                            'next_url': next_url}
                else:
                    return {"art_list_url": art_list_url}

            else:
                proxies = {
                    'https': 'https://' + str(get_proxie())
                }
                return get_url_list(list_url, headers, proxies)
        except:
            proxies = {
                'https': 'https://' + str(get_proxie())
            }
            return get_url_list(list_url, headers, proxies)


# def get_one_page(url, headers, proxy):
#     print('分析帖子：', url)
#     try:
#         response = requests.get(url, headers=headers, proxies=proxy, timeout=8,
#                                 verify=False)  # , allow_redirects=False verify是否验证服务器的SSL证书
#         if response.status_code == 200:
#             if '您的访问出现异常' not in response.text:
#                 print('代理可用，执行下一步')
#                 urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#                 return response.text
#             else:
#                 print('您的访问出现异常，请更换代理IP')
#                 proxy = {
#                     'https': 'https://' + str(get_proxie())
#                 }
#                 return get_one_page(url, headers, proxy)
#
#         if response.status_code == 302:
#             print('302')
#             proxy = {
#                 'https': 'https://' + str(get_proxie())
#             }
#             return get_one_page(url, headers, proxy)
#
#         if response.status_code == 404:
#             print('404')
#             if '文章被删除' in response.text:
#                 return None
#             else:
#                 proxy = {
#                     'https': 'https://' + str(get_proxie())
#                 }
#                 print('使用代理IP：', proxy)
#                 return get_one_page(url, headers, proxy)
#     except:
#         proxy = {
#             'https': 'https://' + str(get_proxie())
#         }
#         return get_one_page(url, headers, proxy)


def parse_art(url):
    while True:
        try:
            browser.get(url)
            Element = WebDriverWait(browser, 100).until(EC.presence_of_element_located((By.XPATH, "//h1")))
            break
        except:
            pass
    browser.implicitly_wait(10)
    js = "var q=document.documentElement.scrollTop=10000"
    # 执行脚本
    browser.execute_script(js)
    time.sleep(1.5 * random.uniform(1, 3))
    html = browser.page_source
    while "您的访问出现异常" in html:
        print("出现验证，休眠")
        browser.find_element_by_xpath('//div[@class="geetest_radar_tip"]')
        time.sleep(1 * 60)
        try:
            browser.find_element_by_xpath('//div[@class="geetest_radar_tip"]').click()
        except:
            pass
        browser.get(url)
        html = browser.page_source
    return html


def parse_one_page(url, html):
    print("解析帖子", url)
    # # html = str(html)
    # if '本田摩托车论坛' not in html:
    #     item = {'collection': "汽车之家(4.1)", 'comment_url': url}  # 存入被重定向URL
    #     return save_to_db(item)
    try:
        tree = etree.HTML(html)
        topic = tree.xpath('//*[@id="F0"]')  # 获取主贴
        TopicInfo = {}
        if topic:
            forum = tree.xpath('//*[@id="consnav-root"]/div/span[1]/a/text()')[0]
            # print('版块：' + forum)
            TopicInfo['sonbbs_name'] = forum
            for info in topic:
                TopicInfo['comment_url'] = url
                # print('帖子链接：' + url)
                topic_title = info.xpath('//*[@id="consnav"]/span[4]/text()')[0]
                TopicInfo['title'] = topic_title
                comtpath = info.xpath('.//div[@class="conttxt"]')[0]
                comtstr = comtpath.xpath('string(.)').strip()
                TopicInfo['comment_detail'] = comtstr
                topic_time = info.xpath('//*[@id="F0"]/div[3]/div[1]/span[2]/text()')[0]
                # print('发布时间：' + str(topic_time))
                TopicInfo['push_time'] = topic_time
                # 楼主相关信息
                user_name = info.xpath('//*[@id="F0"]/div[2]/ul[1]/li[1]/a/text()')[0].strip()
                # print('用户名：' + user_name)
                TopicInfo['username'] = user_name
                user_from = info.xpath('//*[@id="F0"]/div[2]/ul[2]/li[6]/a/text()')
                if user_from:
                    user_from = user_from[0]
                    # print('来自：' + user_from)
                    TopicInfo['userlocation'] = user_from
                else:
                    # print('没有地区')
                    TopicInfo['userlocation'] = None
                TopicInfo['usergender'] = None
                TopicInfo['userage'] = None
                TopicInfo['bbs_name'] = '汽车之家'
                TopicInfo['comment_url'] = url
                TopicInfo['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                TopicInfo['car_type'] = None
                TopicInfo['collection'] = "(汽车之家问答)自动驾驶"
                save_to_db(TopicInfo)

        title = tree.xpath('//div[@id="consnav"]/span[4]/text()')[0]
        bbsname = tree.xpath('//div[@id="consnav"]/span[2]/a/text()')[0]
        for each in tree.xpath('//div[@id="maxwrap-reply"]/div[@class="clearfix contstxt outer-section"]'):
            username = each.xpath('.//li[@class="txtcenter fw"]/a/text()')[0].strip()
            userloc = each.xpath('.//ul[@class="leftlist"]/li[6]/a/text()')
            uid = each.xpath('./@uid')[0]
            userurl = "https://i.autohome.com.cn/{}/info".format(uid)
            usermsg = [None, None, None]  # self.parse_user(userurl)
            pushtime = each.xpath('.//span[@xname="date"]/text()')[0]
            comtpath = each.xpath('.//div[@class="x-reply font14"]')[0]
            comtstr = comtpath.xpath('string(.)').strip()
            item = {}
            item['title'] = title
            item['bbs_name'] = '汽车之家'
            item['sonbbs_name'] = bbsname
            item['username'] = username
            item['comment_detail'] = comtstr
            item['comment_url'] = url
            item['push_time'] = pushtime
            item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item['car_type'] = None
            item['collection'] = "(汽车之家问答)自动驾驶"  # 设置存入表名
            item['usergender'] = usermsg[0]
            if userloc:
                item['userlocation'] = userloc[0]
            else:
                item['userlocation'] = None
            item['userage'] = usermsg[2]
            save_to_db(item)

        if tree.xpath('//a[@class="afpage"]'):
            headers = {
                'User-Agent': get_randon_ua(),
                'Host': 'club.autohome.com.cn',
                'Upgrade - Insecure - Requests': '1',
                'Accept': 'text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, image / apng, * / *;q = 0.8',
                'Accept - Encoding': 'gzip',
                'Accept - Language': 'zh - CN, zh;q = 0.9, en;q = 0.8',
                'Cache - Control': 'max - age = 0',
                'Connection': 'close',
            }
            proxy = {'https': 'https://' + str(get_proxie())}
            url = 'https://club.autohome.com.cn' + tree.xpath('//a[@class="afpage"]/@href')[1]
            html = parse_art(url)
            if html:
                parse_one_page(url, html)
    except Exception as e:
        print("解析失败:", 'url', e.__traceback__.tb_lineno, e)
        item = {'collection': "(汽车之家)自动驾驶", 'comment_url': "解析失败:" + url}  # 存入解析失败URL
        return save_to_db(item)


def parse_time(pushtime):
    if re.search(r"天前", pushtime):
        num = int(re.search(r"\d+", pushtime).group())
        sec = num * 86400
        pushtime = time.strftime("%Y-%m-%d", time.localtime(time.time() - sec))
    if re.search('小时前', pushtime):
        NUM = int(re.search('\d+', pushtime).group())
        sec = NUM * 60 * 60
        today = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - sec))
        pushtime = today
    if re.search('分钟前', pushtime):
        NUM = int(re.search('\d+', pushtime).group())
        sec = NUM * 60
        today = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - sec))
        pushtime = today
    return pushtime


def save_to_db(item):
    db_url = "localhost"
    db_name = "autohome"
    db = MongoClient(host=db_url)[db_name]
    try:
        db[item['collection']].insert(dict(item))
        print("插入数据库成功")
    except Exception as e:
        print('插入数据库出错,{},{}'.format(item['collection'], e))


def main(url):
    headers = {
        'User-Agent': get_randon_ua(),
        'Host': 'sou.autohome.com.cn',
        'Upgrade - Insecure - Requests': '1',
        'Accept': 'text / html, application / xhtml + xml, application / xml;q = 0.9, image / webp, image / apng, * / *;q = 0.8',
        'Accept - Encoding': 'gzip',
        'Accept - Language': 'zh - CN, zh;q = 0.9, en;q = 0.8',
        'Cache - Control': 'max - age = 0',
        'Connection': 'close',
    }
    conn = pymongo.MongoClient(host="localhost", port=27017)
    db = conn["autohome"]
    proxy = {'https': 'https://' + str(get_proxie())}
    urls = get_url_list(url, headers, proxy)
    for url in urls["art_list_url"]:
        crawled_url = db["(汽车之家问答)自动驾驶"].find_one({"comment_url": url})
        if crawled_url:
            print(crawled_url["comment_url"], "已抓取")
            continue
        print('问答：', url)
        # headers['Host'] = 'zhidao.autohome.com.cn'
        # headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
        # 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
        html = parse_art(url)
        if html:
            parse_one_page(url, html)
    try:
        next_url = urls["next_url"]
        if next_url:
            main(next_url)
    except:
        pass


if __name__ == '__main__':
    KW_LIST = ["自动驾驶", "无人驾驶", "智能网联汽车",
               "自动驾驶 L3级别", "自动驾驶 L4级别",
               "无人驾驶出租车", "视觉融合自动驾驶",
               "V2X 自动驾驶", "激光雷达 自动驾驶", "深度学习 自动驾驶",
               "高精度地图 自动驾驶", "路径规划 自动驾驶", "AI 自动驾驶",
               "算法 自动驾驶", "自动驾驶牌照", "自动驾驶示范区",
               "自动驾驶示范运营", "自动泊车", "自动驾驶智慧交通",
               "无人驾驶小镇", "自动驾驶5G示范区", "自动驾驶智能化"
               ]
    start_urls = []
    for kw in KW_LIST:
        gb_kw = kw.encode("gb2312")
        url_kw = parse.quote(gb_kw)
        start_urls.append("https://sou.autohome.com.cn/zhidao?q={}".format(url_kw))
    for url in start_urls:
        main(url)
    # pool=Pool(3)
    # pool.map(main,start_urls)
    # pool.close()
    # pool.join()
