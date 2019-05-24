#!/usr/bin/env python 3
# encoding: utf-8
from time import time
import os
import pymongo
import requests
import socket
from lxml import etree
import re
import json
import csv
import random
import time
import urllib3
from multiprocessing import Pool
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
START_TIME= "2017-01-01"


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
            if '评论' in str(art_list.text):  # 设置标志性文本防止被重定向
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
                    next_url = 'https://sou.autohome.com.cn/wenzhang' + next_path[0]
                    return {"art_list_url":art_list_url,
                            'next_url':next_url}
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
            if '文章被删除' in response.text:
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


def parse_time(pushtime):
    if re.search(r"天前", pushtime):
        num = int(re.search(r"\d+", pushtime).group())
        sec = num*86400
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


def parse_news_page(url, html):
    print("解析新闻", url)
    try:
        tree = etree.HTML(html)
        ArtInfo = {}
        title = tree.xpath('//h1/text()')[0].strip()
        ArtInfo["title"] = title
        ArtInfo['sonbbs_name'] = None
        ArtInfo['comment_url'] = url
        print('标题：' + title)
        Artpath = tree.xpath('//*[@id="articleContent"]')[0]
        Artstr = Artpath.xpath('string(.)').strip()
        ArtInfo['comment_detail'] = Artstr
        Art_time = tree.xpath('//*[@class="time"]/text()')[0].strip()
        Art_time = parse_time(Art_time)
        Art_time = Art_time.replace("年",'-').replace("月","-").replace("日",'')
        ArtInfo['push_time'] = Art_time
        user_name = None
        try:
            user_name = tree.xpath('//a[@class="name"]/text()')[0]
        except:
            pass
        ArtInfo['username'] = user_name
        ArtInfo['userlocation'] = None
        ArtInfo['usergender'] = None
        ArtInfo['userage'] = None
        ArtInfo['bbs_name'] = '汽车之家'
        ArtInfo['comment_url'] = url
        ArtInfo['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        ArtInfo['car_type'] = None
        ArtInfo['collection'] = "(汽车之家文章)自动驾驶"
        if Art_time > START_TIME:
            save_to_db(ArtInfo)

        # 处理评论
        try:
            count = tree.xpath('//span[@id="reply-count1"]/text()')[0]
        except:
            # 无评论
            return None
        if int(count) > 10:
            comt_url = "https:"+tree.xpath('//a[@id="reply-all-btn1"]/@href')[0]
            return parse_news_comments(comt_url)

        elif int(count) != 0:
            bbsname = None
            for index,each in enumerate(tree.xpath('//dl[@id="reply-list"]//dt')):
                username = each.xpath('./span[1]/a[1]/text()')[0]
                pushtime = each.xpath('./span[2]/text()[1]')[0].replace("[",'')
                pushtime = parse_time(pushtime)
                if pushtime < START_TIME:
                    break
                comtstr = tree.xpath('//dl[@id="reply-list"]//dd[{}]/@datacontent'.format(index+1))[0]
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
                item['collection'] = "(汽车之家文章)自动驾驶"  # 设置存入表名
                item['usergender'] = None
                item['userlocation'] = None
                item['userage'] = None
                save_to_db(item)
    except Exception as e:
        print("解析失败:",'url',e.__traceback__.tb_lineno,e)
        item = {'collection': "(汽车之家文章)自动驾驶:解析失败", 'comment_url': + url}  # 存入解析失败URL
        return save_to_db(item)


def parse_news_comments(url):
    html = parse_art(url)
    if html:
        tree = etree.HTML(html)
        title = tree.xpath('//h1/a[1]/text()')[0]
        bbsname = None
        for index, each in enumerate(tree.xpath('//dl[@id="reply-list"]//dt')):
            try:
                username = each.xpath('./span[1]/a[1]/text()')[0]
                pushtime = each.xpath('./span[2]/text()[1]')[0].replace("[", '')
                pushtime = parse_time(pushtime)
                if pushtime < START_TIME:
                    break
                comtstr = tree.xpath('//dl[@id="reply-list"]//dd[{}]/@datacontent'.format(index+1))[0]
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
                item['collection'] = "(汽车之家文章)自动驾驶"  # 设置存入表名
                item['usergender'] = None
                item['userlocation'] = None
                item['userage'] = None
                save_to_db(item)
            except Exception as e:
                print(e.__traceback__.tb_lineno,e)


def parse_chejiahao_comments(more_url):
    html = parse_art(more_url)
    if html:
        tree = etree.HTML(html)
        title = tree.xpath('//div[@class="all_com_title"]/span/a/text()')[0]
        bbsname = None
        for index, each in enumerate(tree.xpath('//dl[@class="rev_dl"]//dt')):
            try:
                username = each.xpath('.//span[@class="rmembername-span"]/text()')[0]
                try:
                    pushtime = each.xpath('./span[1]/text()[3]')[0].strip()
                except:
                    pushtime = each.xpath('./span[1]/text()[2]')[0].strip()
                pushtime = parse_time(pushtime)
                if pushtime < START_TIME:
                    break
                comtstr = tree.xpath('//dl[@class="rev_dl"]//dd[{}]/p/text()'.format(index+1))[0]
                item = {}
                item['title'] = title
                item['bbs_name'] = '汽车之家'
                item['sonbbs_name'] = bbsname
                item['username'] = username
                item['comment_detail'] = comtstr
                item['comment_url'] = more_url
                item['push_time'] = pushtime
                item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item['car_type'] = None
                item['collection'] = "(汽车之家文章)自动驾驶"  # 设置存入表名
                item['usergender'] = None
                item['userlocation'] = None
                item['userage'] = None
                save_to_db(item)
            except Exception as e:
                print(e.__traceback__.tb_lineno,e)


def parse_chejiahao(url,html):
    print("解析车家号", url)
    try:
        tree = etree.HTML(html)
        ArtInfo = {}
        try:
            title = tree.xpath('//div[@class="title"]/text()')[0]
        except:
            title = None
        ArtInfo["title"] = title
        ArtInfo['sonbbs_name'] = None
        ArtInfo['comment_url'] = url
        Artpath = tree.xpath('//*[@class="introduce"]')[0]
        Artstr = Artpath.xpath('string(.)').strip()
        ArtInfo['comment_detail'] = Artstr
        Art_time = tree.xpath('//div[@class="articleTag"]/span[3]/text()')[0]
        Art_time = parse_time(Art_time)
        ArtInfo['push_time'] = Art_time
        user_name = tree.xpath('//div[@class="articleTag"]/span[1]/text()')[0]
        ArtInfo['username'] = user_name
        ArtInfo['userlocation'] = None
        ArtInfo['usergender'] = None
        ArtInfo['userage'] = None
        ArtInfo['bbs_name'] = '汽车之家'
        ArtInfo['comment_url'] = url
        ArtInfo['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        ArtInfo['car_type'] = None
        ArtInfo['collection'] = "(汽车之家文章)自动驾驶"
        if Art_time > START_TIME:
            save_to_db(ArtInfo)
        # 处理评论
        try:
            re_count = tree.xpath('//*[@id="replyCanyueCount"]/text()')[0].replace("(","").replace(")","")
            if re_count and int(re_count) > 3:
                more_url = "https://chejiahao.autohome.com.cn" + tree.xpath('//a[@class="see_more_comment"]/@href')[0]
                if more_url:
                    return parse_chejiahao_comments(more_url)
        except:
            # 无更多评论
            pass
        comt_path = tree.xpath('//dl[@class="rev_dl"]')
        if comt_path != []:
            bbsname = None
            for index, each in enumerate(tree.xpath('//dl[@class="rev_dl"]//dt')):
                username = each.xpath('.//span[@class="rmembername-span"]/text()')[0]
                try:
                    pushtime = each.xpath('./span[1]/text()[3]')[0].strip()
                except:
                    pushtime = each.xpath('./span[1]/text()[2]')[0].strip()
                pushtime = parse_time(pushtime)
                if pushtime < START_TIME:
                    break
                comtstr = tree.xpath('//dl[@class="rev_dl"]//dd[{}]/p/text()'.format(index+1))[0]
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
                item['collection'] = "(汽车之家文章)自动驾驶"  # 设置存入表名
                item['usergender'] = None
                item['userlocation'] = None
                item['userage'] = None
                save_to_db(item)
    except Exception as e:
        print("解析失败:", url, e.__traceback__.tb_lineno, e)
        item = {'collection': "(汽车之家文章)自动驾驶:解析失败", 'comment_url': url}  # 存入解析失败URL
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


def parse_art(url):
    global browser
    while True:
        try:
            browser.get(url)
            Element = WebDriverWait(browser, 100).until(EC.presence_of_element_located((By.XPATH, "//body")))
            break
        except:
            pass

    js = "var q=document.documentElement.scrollTop=10000"
    # 执行脚本
    browser.execute_script(js)
    time.sleep(1.5*random.uniform(1,3))
    html = browser.page_source
    while "您的访问出现异常" in html:
        print("出现验证，休眠")
        time.sleep(5*60)
        browser.get(url)
        html = browser.page_source
    return html


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
    proxy = {'https': 'https://' + str(get_proxie())}
    urls = get_url_list(url, headers, proxy)
    for url in urls["art_list_url"]:
        conn = pymongo.MongoClient(host="localhost", port=27017)
        db = conn["autohome"]
        crawled_url = db["(汽车之家文章)自动驾驶"].find_one({"comment_url": url})
        if crawled_url:
            print(crawled_url["comment_url"],"已抓取")
            continue
        print('文章：', url)
        html = parse_art(url)
        if html and "news" in url:
            parse_news_page(url, html)
        if html and "chejiahao" in url:
            parse_chejiahao(url, html)
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
               "无人驾驶小镇", "自动驾驶5G示范区", "自动驾驶智能化" ]
    start_urls = []
    for kw in KW_LIST:
        gb_kw = kw.encode("gb2312")
        url_kw = parse.quote(gb_kw)
        start_urls.append("https://sou.autohome.com.cn/wenzhang?q={}".format(url_kw))
    for url in start_urls:
        main(url)
