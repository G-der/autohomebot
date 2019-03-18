import time
import scrapy
from scrapy.spiders import Spider
from datetime import datetime

from autohomebot.items import ArticleItem


class BBS110Spider(Spider):
    name = "110bbs"
    start_time = "2019-01-01"
    start_time_date = datetime.strptime(start_time, "%Y-%m-%d")
    base_url = 'http://bbs.110.com/'
    start_urls = [
        'http://bbs.110.com/forum-48-1.html',
        # 'http://bbs.110.com/viewthread.php?tid=105162&extra=&page=1'
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
        # 解析帖子列表页

        try:
            while True:
                for each in response.xpath('//tbody[starts-with(@id,"normalthread_")]'):
                    push_time_str = each.xpath('.//td[@class="lastpost"]/em/a/text()').extract_first()
                    push_time_date = datetime.strptime(push_time_str, "%Y-%m-%d %H:%S")
                    if push_time_date >= self.start_time_date:
                        url_str = each.xpath('.//th[@class="common" or @class="hot"]/span[1]/a/@href').extract_first()
                        full_url = self.base_url + url_str
                        yield scrapy.Request(full_url, callback=self.parse_detail)
                    else:  # 如有不符合条件的直接结束函数
                        return

                # 如果遍历完成则请求下一页
                next_page = response.xpath('//div[@class="pages_btns"][1]//a[@class="next"]/@href').extract_first()
                if next_page:
                    next_url = self.base_url + next_page
                    yield scrapy.Request(next_url, callback=self.parse)
                return
        except Exception as e:
            print(e.__traceback__.tb_lineno, ":", e)

    def parse_detail(self, response):
        # 解析帖子详情页
        try:
            if response.xpath('//a[@class="next"]') and not response.xpath('//a[@class="prev"]'):  # 若存在下页且不存在上页，直接翻页到最后
                last_page_url = response.xpath(
                    '//div[@class="pages_btns"][1]/div[@class="pages"]/a[last()]/@href').extract_first()
                last_page_url = self.base_url + last_page_url
                yield scrapy.Request(last_page_url, callback=self.parse_detail)
                return
            title = response.xpath('//h1/text()').extract_first()
            item_num = 0
            while True:  # 倒序遍历回复或帖子
                try:
                    reply = response.xpath('//div[@class="mainbox viewthread"][last()-{}]'.format(item_num))
                    if not reply:  # 遍历完成，往前翻页
                        before_page_url = response.xpath(
                            '//div[@class="pages_btns"][1]/div[@class="pages"]/a[@class="prev"]/@href').extract_first()
                        if before_page_url:
                            before_page_url = self.base_url + before_page_url
                            yield scrapy.Request(before_page_url, callback=self.parse_detail)
                        break
                    # 解析元素
                    item = ArticleItem()
                    item["title"] = title
                    item["author"] = reply.xpath('.//td[@class="postauthor"]/cite/a/text()').extract_first()
                    push_time_str = reply.xpath('.//div[@class="postinfo"]/text()[5]').extract_first().strip()
                    push_time_str = push_time_str.replace("发表于 ", '')
                    push_time_date = datetime.strptime(push_time_str, "%Y-%m-%d %H:%S")
                    if push_time_date < self.start_time_date:
                        return
                    item["push_time"] = push_time_date
                    item["source"] = None
                    art_path = reply.xpath('.//div[@class="postmessage defaultpost"]')
                    item["detail"] = art_path.xpath('string(.)').extract_first().strip()
                    item["url"] = response.url
                    item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    item['collection'] = "110法律咨询"
                    item['kw'] = None
                    item['type'] = None
                    yield item
                    item_num += 1
                except Exception as e:
                    print("解析失败", e.__traceback__.tb_lineno, e)
                    break
        except Exception as e:
            print("解析失败", e.__traceback__.tb_lineno, e)
