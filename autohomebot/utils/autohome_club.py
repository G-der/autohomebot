#!/usr/bin/env python 3
# encoding: utf-8
from time import time
from concurrent.futures import ThreadPoolExecutor
import os
import requests
import socket
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout
from lxml import etree
import re
import json
import csv
import random
import time
import urllib3
from multiprocessing import Pool
from pymongo import MongoClient

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
            topic_list_url = []
            club_list = requests.get(list_url, headers=headers, timeout=8, proxies=proxy)
            if '本田摩托车论坛' in str(club_list.text):
                print('解析成功，正在获取帖子链接', list_url)
                pattern = re.compile('<dl.*?list_dl.*?lang.*?">.*?<a.*?href="(.*?)">.*?</dl>', re.S)
                items = re.findall(pattern, club_list.text)
                for item in items:
                    if '#pvareaid' in item:
                        pass
                    else:
                        topic_url = 'https://club.autohome.com.cn' + item
                        topic_list_url.append(topic_url)
            else:
                proxies = {
                    'https': 'https://' + str(get_proxie())
                }
                return get_url_list(list_url, headers, proxies)
            return topic_list_url
        except:
            proxies = {
                'https': 'https://' + str(get_proxie())
            }
            return get_url_list(list_url, headers, proxies)


def get_one_page(url, headers, proxy):
    print('分析帖子：', url)
    try:
        response = requests.get(url, headers=headers, proxies=proxy, timeout=8,
                                verify=False)  # , allow_redirects=False verify是否验证服务器的SSL证书
        if response.status_code == 200:
            if '您的访问出现异常' not in response.text:
                print('代理可用，执行下一步')
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                return response.text
            else:
                print('您的访问出现异常，请更换代理IP')
                proxy = {
                    'https': 'https://' + str(get_proxie())
                }
                return get_one_page(url, headers, proxy)

        if response.status_code == 302:
            print('302')
            proxy = {
                'https': 'https://' + str(get_proxie())
            }
            return get_one_page(url, headers, proxy)

        if response.status_code == 404:
            print('404')
            if '帖子被删除' in response.text:
                return None
            else:
                proxy = {
                    'https': 'https://' + str(get_proxie())
                }
                print('使用代理IP：', proxy)
                return get_one_page(url, headers, proxy)
    except:
        proxy = {
            'https': 'https://' + str(get_proxie())
        }
        return get_one_page(url, headers, proxy)


def parse_one_page(url, html):
    print("解析帖子", url)
    # html = str(html)
    if '本田摩托车论坛' not in html:
        item = {'collection': "汽车之家(3.19)", 'comment_url': url}
        return save_to_db(item)
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
                print('帖子链接：' + url)
                topic_title = info.xpath('//*[@id="consnav"]/span[4]/text()')[0]
                TopicInfo['title'] = topic_title
                print('标题：' + topic_title)
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
                TopicInfo['collection'] = "汽车之家(3.19)"
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
            item['collection'] = "汽车之家(3.19)"
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
            html = get_one_page(url, headers, proxy)
            if html:
                parse_one_page(url, html)
    except Exception as e:
        print("解析失败:",'url',e.__traceback__.tb_lineno,e)
        item = {'collection': "汽车之家(3.19)", 'comment_url': "解析失败:"+url}
        return save_to_db(item)



# def save_to_csv(item):
#     headers = ['topic_url', 'forum', 'topic_title', 'topic_time', 'topic_views', 'topic_replys', 'topic_seal', 'user_name', 'user_url','user_topic_num', 'user_replys_num','user_from','user_car','followCount','praise_num']
#     file_path = 'autohome_club.csv'
#     if os.path.exists(file_path):
#         with open(file_path, 'a', encoding='utf-8',newline='') as f:
#             writer = csv.DictWriter(f, fieldnames=headers)
#             writer.writerow(item)
#             print('保存成功')
#     else:
#         with open(file_path, 'w+', encoding='utf-8',newline='') as f:
#             writer = csv.DictWriter(f, fieldnames=headers)
#             writer.writeheader()
#             writer.writerow(item)
#             print('保存成功')

def save_to_db(item):
    db_url = "localhost"
    db_name = "autohome"
    db = MongoClient(host=db_url)[db_name]
    try:
        db[item['collection']].insert(dict(item))
        print("插入数据库成功")
    except Exception as e:
        print('插入数据库出错,{},{}'.format(item['collection'], e))


def get_one_url(page):
    # for x in page:
    url = 'https://club.autohome.com.cn/bbs/forum-o-210763-{}.html?orderby=dateline'.format(page)
    return url


def main(page):
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
    url_list = get_one_url(page)
    urls = get_url_list(url_list, headers, proxy)
    for url in urls:
        print('帖子：', url)
        html = get_one_page(url, headers, proxy)
        if html:
            parse_one_page(url, html)


if __name__ == '__main__':
    start_time = time.time()
    groups = []
    for x in range(58, 1, -1):
        groups.append(x)  # [x for x in range(89,0,-1)]
    pool = Pool(3)
    pool.map(main, groups)
    pool.close()
    pool.join()
    end_time = time.time()
    print(start_time, end_time - start_time)
