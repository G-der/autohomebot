from lxml import etree
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re
import time
from autohomebot.items import BaseItem
import requests
from autohomebot.settings import DEFAULT_REQUEST_HEADERS


class Moto8Spider(CrawlSpider):
    # spider的唯一名称
    name = 'moto8'
    allowed_domains = ['bbs.moto8.com']
    # 开始爬取的url
    start_urls = [
        "http://bbs.moto8.com/forum.php?gid=360",  # 摩托车品牌
        "http://bbs.moto8.com/forum.php?gid=201",  # 摩托文化
        "http://bbs.moto8.com/forum.php?gid=44",  # 机车
        "http://bbs.moto8.com/forum.php?gid=731",  # 车型
        "http://bbs.moto8.com/forum.php?gid=627",  # 地方
    ]
    # 从页面需要提取的url 链接(link)
    pages = LinkExtractor(allow="forum-")
    links = LinkExtractor(restrict_xpaths=['//tbody[starts-with(@id,"normalthread_")]', '//div[@class="pg"]'],
                          allow="thread-")

    # 设置解析link的规则，callback是指解析link返回的响应数据的的方法
    rules = [Rule(link_extractor=pages, follow=True),
             Rule(link_extractor=links, callback="parseContent", follow=True)]

    def info(self, message, isPrint=True):
        # 控制台显示消息
        if isPrint == True:
            print('[' + time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time())) + '][INFO]' + message)

        # Log文件输出
        self.logger.info(message)

    def warning(self, message, logOutput=True):
        # 控制台显示消息
        print('[' + time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time())) + '][WARNING]' + message)

        # Log文件输出
        if logOutput == True:
            self.logger.warning(message)

    def error(self, message, logOutput=True):
        # 控制台显示消息
        print('[' + time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time())) + '][ERROR]' + message)

        # Log文件输出
        if logOutput == True:
            self.logger.error(message)


    def parseContent(self, response):
        title = response.xpath('//h1/span/text()').extract_first()
        sonbbs_name = response.xpath('//div[@id="pt"]/div[@class="z"]/a[4]/text()').extract_first()
        try:
            for each in response.xpath('//table[starts-with(@id,"pid")]'):
                username = each.xpath('.//a[@class="xw1"]/text()').extract_first()
                # 尝试获取用户所在地
                user_loc = None
                try:
                    userurl = each.xpath('.//div[@class="authi"]/a[starts-with(@href,"space")]/@href').extract_first()
                    user_id = re.search(r'\d+', userurl).group()
                    user_profile = "http://bbs.moto8.com/home.php?mod=space&uid={}&do=profile".format(user_id)
                    res = requests.get(user_profile, headers=DEFAULT_REQUEST_HEADERS)
                    html = etree.HTML(res.text)
                    user_loc = html.xpath('//ul[@class="pf_l cl"]/li[1]/text()')[0]
                except:
                    pass

                pushtime = each.xpath('.//div[@class="authi"]/em/text()').extract_first()
                compath = each.xpath('.//td[@class="t_f"]')
                comtstr = compath.xpath('string(.)').extract_first()

                item = BaseItem()
                item['title'] = title
                item['bbs_name'] = '摩托吧'
                item['sonbbs_name'] = sonbbs_name
                item['username'] = username
                item['comment_detail'] = comtstr
                item['comment_url'] = response.url
                item['push_time'] = pushtime
                item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item['car_type'] = None
                item['collection'] = "摩托吧"
                item['usergender'] = None
                item['userlocation'] = user_loc
                item['userage'] = None
                yield item
        except Exception as e:
            self.error('【parse_detail出错】url:{}; line{}:{}'.format(response.url, e.__traceback__.tb_lineno, e))

