import re
import time
import scrapy

from autohomebot.items import ArticleItem


class TecSpider(scrapy.Spider):
    name = 'rmauto'
    start_urls = [
        'http://auto.people.com.cn/GB/1049/index1.html',  # 国内
        'http://auto.people.com.cn/GB/173005/index1.html',  # 国际
        'http://auto.people.com.cn/GB/1051/index1.html',  # 政策
        'http://auto.people.com.cn/GB/14555/index1.html',  # 行业动态
        'http://auto.people.com.cn/GB/1052/25089/index1.html',  # 价格行情
        'http://auto.people.com.cn/GB/10309/120257/index1.html',  # 汽车试驾
        'http://auto.people.com.cn/GB/1052/81336/index1.html'  # 上市新车
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
        # 请求新闻详情
        for each in response.xpath('//dt'):
            art_url = 'http://auto.people.com.cn' + each.xpath('./a/@href').extract_first()
            yield scrapy.Request(url=art_url, callback=self.parse_art)

        if response.xpath('//a[text()="下一页"]'):  # 若存在下一页
            page_num = re.search(r'index(\d+)', response.url)
            if page_num:
                page_num = str(int(page_num.group(1)) + 1)
                next_url = re.sub('index(\d+)', 'index' + page_num, response.url)
                yield scrapy.Request(next_url, callback=self.parse)
            # else:
            #     next_url = re.sub('index', 'index1', response.url)

    def parse_art(self, response):
        start_time = '2019年03月01日'  # TODO 设置起始时间
        try:
            push_time_str = response.xpath('//div[@class="box01"]/div[@class="fl"]/text()').extract_first()
            push_time = push_time_str.replace('  来源：', '')
            if not push_time < start_time:
                item = ArticleItem()
                item["title"] = response.xpath('//h1/text()').extract_first().strip()
                item["author"] = response.xpath('//div[@class="edit clearfix"]/text()').extract_first()
                item["push_time"] = push_time
                source = response.xpath('//div[@class="box01"]/div[@class="fl"]/a/text()').extract_first()
                item["source"] = source
                art_path = response.xpath('//div[@class="box_con"]')
                item["detail"] = art_path.xpath('string(.)').extract_first().strip()

                item["url"] = response.url
                item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item['collection'] = "人民网"
                if 'auto' in response.url:
                    item['type'] = '汽车'
                yield item
        except Exception as e:
            print("解析失败", e.__traceback__.tb_lineno, e)
