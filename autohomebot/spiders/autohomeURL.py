import time
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from autohomebot.items import urlitems
import scrapy



# class MotuomiSpider(CrawlSpider):
#     # spider的唯一名称
#     name = 'autohomeurl'
#     allowed_domains = ['club.autohome.com.cn']
#     # 开始爬取的url
#     start_urls = [
#         "https://club.autohome.com.cn/bbs/forum-o-200063-1.html",  # 摩托车论坛
#     ]
#     # 从页面需要提取的url 链接(link)
#     forums = LinkExtractor(allow="forum-o", restrict_xpaths='//ul[@id="_mch"]')
#
#     # 设置解析link的规则，callback是指解析link返回的响应数据的的方法
#     rules = [
#         Rule(link_extractor=forums, callback="parselinks"),
#     ]
#
#     def info(self, message, isPrint=True):
#         # 控制台显示消息
#         if isPrint == True:
#             print('[' + time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time())) + '][INFO]' + message)
#
#         # Log文件输出
#         self.logger.info(message)
#
#     def warning(self, message, logOutput=True):
#         # 控制台显示消息
#         print('[' + time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time())) + '][WARNING]' + message)
#
#         # Log文件输出
#         if logOutput == True:
#             self.logger.warning(message)
#
#     def error(self, message, logOutput=True):
#         # 控制台显示消息
#         print('[' + time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time())) + '][ERROR]' + message)
#
#         # Log文件输出
#         if logOutput == True:
#             self.logger.error(message)
#
#     def parselinks(self, response):
#         item = urlitems()
#         url = response.url
#         sonbbs_name = response.xpath('//h1/@title').extract_first()
#         if sonbbs_name == "奥迪RS论坛":
#             yield scrapy.Request(url=response.url, callback=self.parselinks)
#         else:
#             item["url"] = url
#             item["name"] = sonbbs_name
#             item["collection"] = 'autohomeurl'
#             yield item


import requests
from lxml import etree
import pandas as pd


def get_aotohomebbsurl():
    headers = {
        'Accept': 'text/html, application/xhtml+xml, */*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,ja-JP;q=0.5',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }
    response = requests.get("https://club.autohome.com.cn/bbs/forum-o-200063-1.html", headers=headers)
    if response.status_code == 200:
        html = etree.HTML(response.text)
        name_list = []
        url_list = []
        moto_path = html.xpath('//ul[@id="_mch"]//a')
        try:
            for each in moto_path:
                name = each.xpath('./@title')[0]
                if name != "摩托车":
                    name += '摩托车论坛'
                else:
                    name += "论坛"
                name_list.append(name)
                baseurl = "https://club.autohome.com.cn"
                url = baseurl + each.xpath('./@href')[0]
                url_list.append(url)
        except Exception as e:
            print("{}:{}".format(e.__traceback__.tb_lineno, e))
        df = pd.DataFrame({"bbsname":name_list, "url":url_list})
        df.to_csv("autohomeurl.csv")


if __name__ == '__main__':
    get_aotohomebbsurl()
