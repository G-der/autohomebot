import re
import time
import scrapy
from scrapy.spiders import Spider

from autohomebot.items import ArticleItem


class XinHuaForumSpider(Spider):
    name = 'xhforum'
    start_urls = [
        'http://forum.home.news.cn/list/50-0-0-1.html',
        # 'http://forum.home.news.cn/detail/141861725/1.html',
        # 'http://forum.home.news.cn/detail/141901726/1.html'
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
        # 解析首页
        start_time = "03-01"
        base_url = 'http://forum.home.news.cn'
        page_num = int(re.search(r'50-0-0-(\d+)', response.url).group(1)) + 1
        page_url = 'http://forum.home.news.cn/list/50-0-0-{}.html'.format(page_num)

        try:
            for each in response.xpath('//dl[@class="item"]'):
                time_str = each.xpath('.//span[@class="fr ti"]/text()').extract_first()
                if time_str is None:
                    time_str = each.xpath('.//span[@class="fl ti"]/text()').extract_first()
                top = each.xpath('.//span[@class="bq zd"]')
                url_str = each.xpath('./dt/a[1]/@href').extract_first()
                url = base_url + url_str
                if top and time_str < start_time:
                    continue
                elif time_str >= start_time:
                    yield scrapy.Request(url, callback=self.parse_detail)
                else:
                    return
            yield scrapy.Request(page_url, callback=self.parse)
        except Exception as e:
            print(e.__traceback__.tb_lineno, ":", e)

    def parse_detail(self, response):
        # 解析帖子详情
        try:
            item = ArticleItem()
            item["title"] = response.xpath('//h1/span[2]/text()').extract_first()
            if item["title"] is None:
                item["title"] = response.xpath('//h1/span/text()').extract_first()
            item["author"] = response.xpath('//ul[@class="de-xx clear"]/li[2]/a/text()').extract_first().strip()
            item["push_time"] = response.xpath('//ul[@class="de-xx clear"]/li[@class="fr"]/span/text()').extract_first()
            source = None
            item["source"] = source
            art_path = response.xpath('//div[@id="message_"]')
            item["detail"] = art_path.xpath('string(.)').extract_first().strip()

            item["url"] = response.url
            item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            item['collection'] = "新华网"
            item['type'] = '帖子'
            yield item

            reply_page = response.xpath('//div[@class="lt-page clear"]')
            if reply_page:  # 多页评论
                for each in response.xpath('//div[@class="lt-page clear"][1]/ul[@class="fl1"]/li'):
                    url_str = each.xpath('./a/@href').extract_first()
                    reply_page_url = 'http://forum.home.news.cn' + url_str
                    yield scrapy.Request(url=reply_page_url, callback=self.parse_reply)

            elif response.xpath('//div[@id="postreply"]/dl'):  # 单页评论
                try:
                    for each in response.xpath('//div[@id="postreply"]/dl'):
                        item = ArticleItem()
                        item["title"] = response.xpath('//h1/span[2]/text()').extract_first()
                        if item["title"] is None:
                            item["title"] = response.xpath('//h1/span/text()').extract_first()
                        item["author"] = each.xpath('./dd/ul[1]/li[1]/a/text()').extract_first().strip()
                        item["push_time"] = each.xpath('./dd/ul[1]/li[2]/span/text()').extract_first()
                        source = None
                        item["source"] = source
                        art_path = each.xpath('./dd/div[@id]')
                        item["detail"] = art_path.xpath('string(.)').extract_first().strip()

                        item["url"] = response.url
                        item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        item['collection'] = "新华网"
                        item['type'] = '帖子回复'
                        yield item
                except Exception as e:
                    print("解析失败", e.__traceback__.tb_lineno, e)
        except Exception as e:
            print("解析失败", e.__traceback__.tb_lineno, e)

    def parse_reply(self, response):
        # 解析帖子回复
        try:
            for each in response.xpath('//div[@id="postreply"]/dl'):
                item = ArticleItem()
                item["title"] = response.xpath('//h1/span[2]/text()').extract_first()
                if item["title"] is None:
                    item["title"] = response.xpath('//h1/span/text()').extract_first()
                item["author"] = each.xpath('./dd/ul[1]/li[1]/a/text()').extract_first().strip()
                item["push_time"] = each.xpath('./dd/ul[1]/li[2]/span/text()').extract_first()
                source = None
                item["source"] = source
                art_path = each.xpath('./dd/div[@id]')
                item["detail"] = art_path.xpath('string(.)').extract_first().strip()

                item["url"] = response.url
                item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item['collection'] = "新华网"
                item['type'] = '帖子回复'
                yield item
        except Exception as e:
            print("解析失败", e.__traceback__.tb_lineno, e)
