#!/usr/bin/env python 3
# encoding: utf-8
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
import time
import urllib3
from multiprocessing import Pool
from pymongo import MongoClient
from urllib import parse
import settingTBDetail as st
from datetime import datetime, timedelta
import scrapy
from scrapy import Request
from scrapy.http import HtmlResponse as hr
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
import requests
from  pynput.mouse import Button, Controller
from win32gui import *

db = MongoClient(host=st.Server)[st.DB]


def add_schema(url):
    if not url.startswith('http'):
        return 'https:'+url
    return url

def get_RequestUrlFormat(url):
    urls={}
    if url.startswith("https://item"):
        urls={5:'https://rate.taobao.com/feedRateList.htm?auctionNumId={}&currentPageNum={}&pageSize=20&rateType=1',
               3:'https://rate.taobao.com/feedRateList.htm?auctionNumId={}&currentPageNum={}&pageSize=20&rateType=0',
               0:'https://rate.taobao.com/feedRateList.htm?auctionNumId={}&currentPageNum={}&pageSize=20&rateType=-1'}
    else:
        urls={99:'https://rate.tmall.com/list_detail_rate.htm?itemId={}&spuId=999&sellerId=835026114&order=3&currentPage={}'}

    return urls
WindowsTitles=[]
def foo(hwnd,mouse):
    #if IsWindow(hwnd) and IsWindowEnabled(hwnd) and IsWindowVisible(hwnd):
    if '亲，访问受限了' in GetWindowText(hwnd):
        WindowsTitles.append(hwnd)   

def getComment(urls):  
    mouse = Controller()
    lstEx=[]
    for u in urls: 
        if u in lstEx:
            print(u)
            continue            
            
        u=add_schema(u.strip()) 
        if u.startswith('https://click'):
            browser.get(u)
            browser.implicitly_wait(timeout)
            u=browser.current_url                
                
        try:
            id=re.search('(\?|&)id=\d{8,}',u).group()[4:]
            item = {}  
            #item['car_type'] = rValue['sonbbs_name'].strip() 
            #item['sonbbs_name'] =rValue['comment_url'].strip()   
            #请求主题                
            header=''
            while True:
                try:
                    r= requests.get(u)
                    time.sleep(2)
                    rs=hr(browser.current_url, body=r.text, encoding="utf-8")
                    header=''.join(rs.xpath("//script[contains(text(),'TShop.setConfig') and not(@type)]/text()").extract()).strip()                        
                        
                    item['title'] = ''.join(rs.xpath("//title/text()").extract()).strip() 
                    item['shop'] =''.join(rs.xpath("//a[@class='slogo-shopname' or text()='进入店铺']/@href").extract()).strip()

                    if header:
                        pinpai=re.search('"brand".*?",',header)
                        if pinpai:
                            item['pinpai'] = pinpai.group()                        
                    else:
                        item['pinpai'] =''.join(rs.xpath("//ul[@class='attributes-list']/li[1]/@title").extract()).strip()                        
                    break               
                except Exception as e:
                        browser.get(u)                         
                        browser.implicitly_wait(timeout)
                            

            #请求Commnet  
            pjs=get_RequestUrlFormat(u)
            #urlFormat='https://rate.tmall.com/list_detail_rate.htm?itemId=40803162830&spuId=999&sellerId=1971116220&order=1&currentPage=18'  
                                 
            for k,v in pjs.items():
                n=0
                maxPage=1 
                item['stars'] = k
                while n<maxPage:
                    n=n+1
                        
                    while True:
                        try:
                            browser.get(v.format(id,n))
                            browser.implicitly_wait(timeout)
                            rs=hr(browser.current_url, body=browser.page_source, encoding="utf-8") 
                            dic=rs.xpath('//body/text()').extract_first() 
                            if "rate.tmall.com:443" in dic or "rate.taobao.com:443" in  dic:
                                    
                                stopUrl=re.search(r'"url":"(.*)"',dic.replace(' ','')).group(1)
                                if not stopUrl.startswith('http'):
                                    stopUrl="https:"+stopUrl
                                browser.get(stopUrl)
                                browser.implicitly_wait(timeout)
                                try:
                                    #WindowsTitles=[]
                                    EnumWindows(foo, 0)
                                    if WindowsTitles:
                                        SetForegroundWindow (WindowsTitles[-1])
                                    time.sleep(5)
                                    #source=browser.find_element_by_xpath("//*[@id='nc_1_n1z']")
                                    #mouse.position = (source.location['x']+12, source.location['y']+85)
                                    mouse.position = (560, 200)

                                    #鼠标移动（x,y）个距离
                                    time.sleep(5)
                                    mouse.press(Button.left)
                                    time.sleep(1)
                                    mouse.move(258, 0)
                                    time.sleep(2)
                                    mouse.release(Button.left)
                                    time.sleep(10)
                                except :
                                    time.sleep(10)
                                continue

                            dic = re.search(r'\((.*)\)',dic)                              
                                
                            if dic:
                                dicComment = dic.group(1)
                                if u.startswith("https://item"):
                                    while True:
                                        try:
                                            data = json.loads(dicComment)
                                            break
                                        except Exception as e:
                                            dicComment = dicComment[:e.pos]+dicComment[e.pos+1:]
                                    maxPage = data['maxPage']
                                    #TBao
                                    for d in data['comments']:
                                        item['push_time'] = d['date']
                                        item['comment_detail'] = d['content']
                                        item['comment_url'] = n    
                                        item['catch_time'] =time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())                            
                                        save_to_db(item)
                                        appendComment = d['appendList']
                                        if appendComment:
                                            for a in appendComment:
                                                item['comment_url'] = n
                                                appendDate = a['dayAfterConfirm']
                                                item['push_time'] = d['date']+"|"+str(appendDate)
                                                item['comment_detail'] = a['content']
                                                item['catch_time'] =time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                                save_to_db(item)
                                            
                                    break
                                else:
                                    while True:
                                        try:
                                            data = json.loads(dicComment)
                                            break
                                        except Exception as e:
                                            dicComment = dicComment[:e.pos]+dicComment[e.pos+1:]
                                        

                                    maxPage = data['rateDetail']['paginator']['lastPage']
                                    #TMall
                                    for d in data['rateDetail']['rateList']:
                                        item['push_time'] = d['rateDate']
                                        item['comment_detail'] = d['rateContent']
                                        item['comment_url'] = n   
                                        item['catch_time'] =time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())                             
                                        save_to_db(item)
                                        appendComment = d['appendComment']
                                        if appendComment:
                                            item['comment_url'] = n
                                            item['push_time'] = appendComment['commentTime']
                                            item['comment_detail'] = appendComment['content']
                                            item['catch_time'] =time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                            save_to_db(item)                                           
                                    break
                                   
                            else:#拦截                                    
                                browser.get(u)                                    
                                time.sleep(20)
                        except Exception as e:
                            browser.get(u)                         
                            browser.implicitly_wait(timeout)
                            #self.logger.error(u) 
                
        except Exception as e:
            pass
            #self.logger.error(u)  
                     
    print("End")
    browser.quit() 

def save_to_db(item):
    
    try:
        db[st.TableName].insert(dict(item))
        print("插入数据库成功")
    except Exception as e:
        print('插入数据库出错,{},{}'.format(st.TableName, e))



def main(url):
    print('帖子：', url)


if __name__ == '__main__':
    start_time = time.time()
    # groups = []
    # for x in range(58, 1, -1):
    #     groups.append(x)  # [x for x in range(89,0,-1)]
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('blink-settings=imagesEnabled=false')
    #chrome_options.add_argument('--proxy-server=127.0.0.1:8080')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_experimental_option('excludeSwitches',['enable-automation'])
    timeout=20
    browser = webdriver.Chrome(chrome_options=chrome_options) 
    wait = WebDriverWait(browser, timeout) 
                    
    browser.get("https://www.taobao.com") 
    time.sleep(60) 
    getComment(st.URLS)