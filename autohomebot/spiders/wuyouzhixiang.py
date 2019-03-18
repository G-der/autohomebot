import time
from datetime import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from autohomebot.items import ArticleItem


class WyzxSpider(CrawlSpider):
    name = "wyzx"
    start_urls = ["http://www.wyzxwk.com/article/ualist/index.html"]
    list_links = LinkExtractor(allow="ualist/index", restrict_xpaths='//div[@class="g-mn m-pages"]')
    art_links = LinkExtractor(allow="www.wyzxwk.com", restrict_xpaths='//ul[@class="m-list"]')

    rules = [
        Rule(list_links, follow=True),
        Rule(art_links, callback='parse_art')
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

    def parse_art(self, response):
        time_str = response.xpath('//div[@class="f-fl"]/span[3]/text()').extract_first()
        push_time = datetime.strptime(time_str, "%Y-%m-%d")
        start_time = datetime.strptime('2019-3-1', "%Y-%m-%d")
        if push_time >= start_time:
            try:
                item = ArticleItem()
                item["title"] = response.xpath('//h1/text()').extract_first().strip()
                item["author"] = response.xpath('//div[@class="f-fl"]/span[1]/text()').extract_first()
                item["push_time"] = time_str
                source = response.xpath('//div[@class="f-fl"]/text()[6]').extract_first().strip()
                item["source"] = source
                art_path = response.xpath('//article')
                item["url"] = response.url
                item["detail"] = art_path.xpath('string(.)').extract_first().strip()
                item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item['collection'] = "乌有之乡网刊"
                yield item
            except Exception as e:
                print("解析失败", e.__traceback__.tb_lineno, e)
