import time
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from autohomebot.items import urlitems


class MotuomiSpider(CrawlSpider):
    # spider的唯一名称
    name = 'imotourl'
    allowed_domains = ['www.i-motor.com.cn']
    # 开始爬取的url
    start_urls = [
        "http://www.i-motor.com.cn/forum-402-1.html",  # 热帖推荐
    ]
    # 从页面需要提取的url 链接(link)
    pages = LinkExtractor(allow="forum-", restrict_xpaths='//div[@id="forumleftside"]')

    # 设置解析link的规则，callback是指解析link返回的响应数据的的方法
    rules = [
        Rule(link_extractor=pages, callback="parselinks"),
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

    def parselinks(self, response):
        item = urlitems()
        url = response.url
        sonbbs_name = response.xpath('//h1/a/text()').extract_first()
        item["url"] = url
        item["name"] = sonbbs_name
        item["collection"] = 'imotourl'
        yield item
