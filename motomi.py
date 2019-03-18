import time
from scrapy.spiders import CrawlSpider, Rule
import re
from scrapy.linkextractors import LinkExtractor
from autohomebot.items import NiumoKBItem


class MotuomiSpider(CrawlSpider):
    # spider的唯一名称
    name = 'motuomi'
    # 开始爬取的url
    start_urls = [
        # "http://www.motorfans.com.cn/forum-189-1.html",  # 幻影150板块
        "http://www.motorfans.com.cn/forum-266-1.html"  # 佳御（甲鱼）板块
    ]
    # 从页面需要提取的url 链接(link)
    pages = LinkExtractor(allow="forum-189-\d+\.html")
    links = LinkExtractor(restrict_xpaths=['//tbody[starts-with(@id,"normalthread_")]'],
                          allow="thread.*\.html")

    # 设置解析link的规则，callback是指解析link返回的响应数据的的方法
    rules = [Rule(link_extractor=pages, callback=None),
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
        """
        解析响应的数据，获取需要的数据字段
        :param response: 响应的数据
        :return:
        """
        try:
            title = response.xpath('//span[@id="thread_subject"]/text()').extract_first()
            for each in response.xpath('//div[@id="ct"]/div[@id="postlist"]/div'):
                # 获取用户名
                username = each.xpath('.//div[@class="authi"]/a[@class="xw1"]/text()').extract_first()
                # 获取并清洗评论详情 TODO 待优化
                comt = None
                try:
                    comt = each.xpath('.//td[@class="t_f"]/node()').extract()
                except:
                    continue
                # patt = re.compile('<.*?>(.*?)<.*?>')
                # comtstrlist = patt.findall(comt)
                comtstr = ''.join(comt).strip()
                rush = ['\r', '<.*?>', '\xa0', '\n']
                for item in rush:
                    comtstr = re.sub(item, '', comtstr)

                # 获取论坛url
                comturl = response.url
                # 获取评论时间
                pushtime = each.xpath('.//div[@class="authi"]/em/text()').extract_first()

                item = NiumoKBItem()
                item['title'] = title
                item['collection'] = '五羊本田二轮'  # TODO 换板块时修改集合名
                item['username'] = username
                if item['username'] is None:
                    continue
                # item['comment_type'] = commenttype
                item['comment_detail'] = comtstr
                item['comment_url'] = comturl
                item['push_time'] = pushtime
                item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item['data_from'] = '摩托迷'
                cartype_patt = re.compile('佳御|甲鱼|幻影|喜鲨|迅鲨')
                item['car_type'] = "幻影"
                try:
                    item['car_type'] = cartype_patt.search(title).group()
                    if item['car_type'] == "甲鱼":
                        item['car_type'] = "佳御"
                except:
                    pass
                yield item
        except Exception as e:
            self.error('【parse_detail出错】{},{}'.format(response.url, e))



