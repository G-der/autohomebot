import scrapy
import time
from autohomebot.items import ArticleItem


class TecSpider(scrapy.Spider):
    name = 'tech'
    start_urls = [
        'http://www.xinhuanet.com/tech/index.htm',  # 科技
        'http://www.xinhuanet.com/auto/index.htm',  # 汽车
        'http://www.xinhuanet.com/energy/index.htm',  # 能源
        'http://www.xinhuanet.com/money/index.htm'  # 金融
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
        for each in response.xpath('//li[@class="clearfix"]'):
            time_str = each.xpath('./div[@class="info"]/span/text()').extract_first()
            if time_str >= start_time:
                url = each.xpath('./h3/a/@href').extract_first()
                yield scrapy.Request(url=url, callback=self.parse_art)

    def parse_art(self, response):
        try:
            item = ArticleItem()
            item["title"] = response.xpath('//div[@class="h-title"]/text()').extract_first().strip()
            item["author"] = response.xpath('//span[@class="p-jc"]/text()[2]').extract_first().strip()
            item["push_time"] = response.xpath('//div[@class="h-info"]/span[1]/text()').extract_first()
            source = response.xpath('//div[@class="h-info"]//em[@id="source"]/text()').extract_first().strip()
            item["source"] = source
            art_path = response.xpath('//div[@id="p-detail"]')
            item["detail"] = art_path.xpath('string(.)').extract_first().strip()

            item["url"] = response.url
            item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item['collection'] = "新华网"
            if "tech" in response.url:
                item['type'] = '科技'
            if 'auto' in response.url:
                item['type'] = '汽车'
            if 'energy' in response.url:
                item['type'] = '能源'
            if 'money' in response.url:
                item['type'] = '金融'
            yield item
        except Exception as e:
            print("解析失败", e.__traceback__.tb_lineno, e)


