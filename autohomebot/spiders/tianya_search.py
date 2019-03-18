import re
import time
import scrapy
from scrapy.spiders import Spider
from autohomebot.items import ArticleItem
import requests
from lxml import etree


class TianyaForumSpider(Spider):
    name = 'tianya'
    kw = "汽车"  # TODO 修改抓取关键字
    start_urls = [
        'http://search.tianya.cn/bbs?q={}&pn=1&s=6'.format(kw),  # 搜索，按时间排序
    ]
    base_url = 'http://bbs.tianya.cn'
    start_time = "2019-03-01"

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
        # 解析搜索页
        try:
            for each in response.xpath('//div[@class="searchListOne"]/ul/li'):
                TZurl = each.xpath('.//h3/a/@href').extract_first()
                if TZurl:
                    yield scrapy.Request(TZurl, callback=self.parse_detail)
            # 判断最后一条帖子的最新回复是否在日期内
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
            }
            last_url = response.xpath('//div[@class="searchListOne"]/ul/li[10]//h3/a/@href').extract_first()
            if last_url is None:  # 若未查询到，再次请求
                yield scrapy.Request(response.url, callback=self.parse, dont_filter=True)
            last_response = requests.get(url=last_url, headers=headers)
            html = etree.HTML(last_response.text)
            if html.xpath('//div[@class="mb15 cf"]/div[@class="atl-pages"]/form'):
                last_page_url = html.xpath('//div[@class="mb15 cf"]/div[@class="atl-pages"]/form/a[last()-1]/@href')[0]
                last_page_url = self.base_url + last_page_url
                last_page_response = requests.get(url=last_page_url, headers=headers)
                html = etree.HTML(last_page_response.text)
            # tiem_path = None
            try:
                time_path = html.xpath('//div[@class="atl-item"][last()]//div[@class="atl-info"]/span[2]/text()')[0]
            except:
                try:  # 无回复，提取帖子发布时间
                    time_path = html.xpath('//div[@class="atl-info"]/span[2]/text()')[0]
                except:  # 提取回答时间
                    time_path = html.xpath('//div[@class="answer-wrapper"]/div[last()]/@js_restime')[0]
            newest_time = time_path.replace('时间：', '')
            if newest_time >= self.start_time:
                next_num = str(int(re.search(r'pn=(\d+)', response.url).group(1)) + 1)
                next_url = re.sub(r'pn=\d+', 'pn={}'.format(next_num), response.url)
                yield scrapy.Request(next_url, callback=self.parse)
        except Exception as e:
            print(e.__traceback__.tb_lineno, ":", e)

    def parse_detail(self, response):
        try:
            if response.xpath('//a[text()="下页"]') and not response.xpath('//a[text()="上页"]'):  # 若存在下页且不存在上页，直接翻页到最后
                last_page_url = response.xpath(
                    '//div[@class="mb15 cf"]/div[@class="atl-pages"]/form/a[last()-1]/@href').extract_first()
                last_page_url = self.base_url + last_page_url
                yield scrapy.Request(last_page_url, callback=self.parse_detail)
                return
            title = response.xpath('//*[@id="post_head"]/h1/span[1]/span/text()').extract_first()
            host_path = response.xpath('//div[@class="atl-item host-item"]')
            if host_path:  # 若存在主贴
                push_time_str = response.xpath('//*[@id="post_head"]/div[2]/div[2]/span[2]/text()').extract_first()
                push_time = push_time_str.replace('时间：', '')
                if push_time > self.start_time:  # 且时间符合
                    item = ArticleItem()
                    item["title"] = title
                    item["author"] = response.xpath(
                        '//*[@id="post_head"]/div[2]/div[2]/span[1]/a[1]/text()').extract_first()
                    item["push_time"] = push_time
                    item["source"] = None
                    art_path = host_path.xpath('.//div[@class="bbs-content clearfix"]')
                    item["detail"] = art_path.xpath('string(.)').extract_first().strip()
                    item["url"] = response.url
                    item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    item['collection'] = "天涯网"
                    item['kw'] = self.kw
                    item['type'] = None
                    yield item

            item_num = 0
            while True:  # 倒序遍历回复或帖子
                try:
                    reply = response.xpath('//div[@class="atl-item"][last()-{}]'.format(item_num))
                    if reply is None:  # 往前翻页
                        before_page_url = response.xpath(
                            '//div[@class="mb15 cf"]/div[@class="atl-pages"]/form/a[text()="上页"]/@href').extract_first()
                        if before_page_url:
                            before_page_url = self.base_url + before_page_url
                            yield scrapy.Request(before_page_url, callback=self.parse_detail)
                        break
                    item = ArticleItem()
                    item["title"] = title
                    item["author"] = reply.xpath('./@_host').extract_first()
                    push_time = reply.xpath('./@js_restime').extract_first()
                    if push_time < self.start_time:
                        break
                    item["push_time"] = push_time
                    item["source"] = None
                    art_path = reply.xpath('.//div[@class="bbs-content"]')
                    item["detail"] = art_path.xpath('string(.)').extract_first().strip()

                    item["url"] = response.url
                    item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    item['collection'] = "天涯网"
                    item['kw'] = self.kw
                    item['type'] = None
                    yield item
                    item_num += 1
                except:
                    break
        except Exception as e:
            print("解析失败", e.__traceback__.tb_lineno, e)
