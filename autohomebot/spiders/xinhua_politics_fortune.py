import json
import re

import scrapy
import time
from autohomebot.items import ArticleItem


class PoliticsSpider(scrapy.Spider):
    name = 'politics'
    start_urls = [
        'http://qc.wa.news.cn/nodeart/list?nid=113352&pgnum=1&cnt=200&tp=1&orderby=1',  # 时政
        'http://qc.wa.news.cn/nodeart/list?nid=11147664&pgnum=1&cnt=200&tp=1&orderby=1',  # 财经
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

    def parse(self, response):
        start_time = '2019-03-01'  # TODO 设置起始时间
        art_count = 0
        try:
            str = re.search(r'({.*})', response.text).group()
            data = json.loads(str)
            for obj in data["data"]["list"]:
                if obj["PubTime"] >= start_time:
                    art_count += 1
                    yield scrapy.Request(url=obj["LinkUrl"], callback=self.parse_art)
        except Exception as e:
            print(e.__traceback__.tb_lineno, ":", e)

        if art_count == 200:  # 若200篇文章均在时间内，则翻页，以月为标准，如时间长，需优化代码
            next_url = re.sub('pgnum=1', 'pgnum=2', response.url)
            yield scrapy.Request(next_url, callback=self.parse())

    def parse_art(self, response):
        try:
            item = ArticleItem()
            try:
                item["title"] = response.xpath('//h1/text()').extract_first()
                item["author"] = response.xpath('//div[@class="edit"]/text()').extract_first().strip()
                item["push_time"] = response.xpath('//div[@class="info"]/span[1]/span[1]/text()').extract_first()
                source = response.xpath('//div[@class="info"]//em[@id="source"]/text()').extract_first().strip()
                item["source"] = source
                art_path = response.xpath('//div[@id="content"]')
                item["detail"] = art_path.xpath('string(.)').extract_first().strip()
            except:
                item["title"] = response.xpath('//div[@class="h-title"]/text()').extract_first()
                item["author"] = response.xpath('//span[@class="p-jc"]/text()[2]').extract_first().strip()
                item["push_time"] = response.xpath('//div[@class="h-info"]/span[1]/text()').extract_first()
                source = response.xpath('//div[@class="h-info"]//em[@id="source"]/text()').extract_first().strip()
                item["source"] = source
                art_path = response.xpath('//div[@id="p-detail"]')
                item["detail"] = art_path.xpath('string(.)').extract_first().strip()
            item["url"] = response.url
            item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item['collection'] = "新华网"
            if 'politics' in response.url:
                item['type'] = '时政'
            if 'fortune' in response.url:
                item['type'] = '财经'
            if 'money' in response.url:
                item['type'] = '金融'
            yield item
        except Exception as e:
            print("解析失败", e.__traceback__.tb_lineno, e)
