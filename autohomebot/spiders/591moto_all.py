from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re
import time
from autohomebot.items import NiumoKBItem, BaseItem
import json


class Moto591(CrawlSpider):
    name = "591mt"
    allowed_domains = ["bbs.591moto.com"]
    start_urls = [
        # "http://bbs.591moto.com/forum-135-1.html",  # 五羊本田品牌论坛
        "http://bbs.591moto.com/forum.php?gid=1",  # 车友交流区
        "http://bbs.591moto.com/forum.php?gid=6",  # 车友生活区
        "http://bbs.591moto.com/forum.php?gid=180"  # 品牌交流区
    ]
    forums = LinkExtractor(allow="forum-", restrict_xpaths=('//div[@class="fl bm"]', '//span[@id="fd_page_top"]'))
    links = LinkExtractor(allow="thread-", restrict_xpaths=('//table[starts-with(@summary,"forum_")]', '//div[@class="pg"]'))

    rules = [
        Rule(forums, follow=True),
        Rule(links, callback="parse591moto", follow=True)
    ]

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

    def parse591moto(self, response):
        title = response.xpath('//h1/span/text()').extract_first()
        sonbbsname = response.xpath('//div[@id="pt"]/div[@class="z"]/a[4]/text()').extract_first()
        try:
            for each in response.xpath('//div[@id="postlist"]/div[starts-with(@id,"post_")]'):
                username = each.xpath('.//div[@class="authi"]/a[@class="xw1"]/text()').extract_first()
                pushtime = each.xpath('.//div[@class="authi"]/em/text()').extract_first()
                if pushtime == "发表于 ":
                    pushtime = each.xpath('.//div[@class="authi"]/em/span/@title').extract_first()
                comtpath = each.xpath('.//td[@class="t_f"]')
                comtstr = comtpath.xpath('string(.)').extract_first()

                item = BaseItem()
                item['title'] = title
                item['bbs_name'] = '591摩托论坛'
                item['sonbbs_name'] = sonbbsname
                item['username'] = username
                item['comment_detail'] = comtstr
                item['comment_url'] = response.url
                item['push_time'] = pushtime
                item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item['car_type'] = None
                item['collection'] = "591摩托"
                item['usergender'] = None
                item['userlocation'] = None
                item['userage'] = None
                yield item
        except Exception as e:
            self.error('【parse_detail出错】url:{}; line{}:{}'.format(response.url, e.__traceback__.tb_lineno, e))
