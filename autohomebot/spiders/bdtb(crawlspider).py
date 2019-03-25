import json
from datetime import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import scrapy
import re
import time
from autohomebot.items import NiumoKBItem, BaseItem


class BDTieba(CrawlSpider):
    name = "bdtb"
    allowed_domains = ["tieba.baidu.com"]
    start_urls = [
        # "https://tieba.baidu.com/f?kw=%E4%BD%B3%E5%BE%A1&ie=utf-8"  # 佳御吧 pn<=1100
        # "https://tieba.baidu.com/f?kw=%E4%BA%94%E7%BE%8A%E6%9C%AC%E7%94%B0&ie=utf-8"  # 五羊本田总吧 pn<=3650
        # "https://tieba.baidu.com/f?kw=冈本&ie=utf-8"  # 冈本吧 pn<=500
        # "https://tieba.baidu.com/f?kw=%D4%C3%BF%E1",  # 悦酷吧
        # "https://tieba.baidu.com/f?ie=utf-8&kw=力帆kp150",  # 力帆kp150吧
        # "https://tieba.baidu.com/f?ie=utf-8&kw=雅马哈巧格i",  # 雅马哈巧格i吧
        # "https://tieba.baidu.com/f?ie=utf-8&kw=光阳劲丽",  # 光阳劲丽吧
        # "https://tieba.baidu.com/f?ie=utf-8&kw=铃木优友",  # 铃木优友吧
        # "https://tieba.baidu.com/f?ie=utf-8&kw=雅马哈尚领",  # 雅马哈尚领吧
        "https://tieba.baidu.com/p/5629760278?pn=2"
    ]

    pages = LinkExtractor(allow="pn=", restrict_xpaths='//div[@id="frs_list_pager"]')
    links = LinkExtractor(allow="/p/\d+", deny='see_lz=1',
                          restrict_xpaths=('//ul[@id="thread_list"]', '//ul[@class="l_posts_num"]'))

    rules = [
        Rule(pages, follow=True),
        Rule(links, callback="parse_reply", follow=True)
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
            self.logger.errorb(message)

    def parse_reply(self, response):
        bbsname = response.xpath('//div[@class="card_title "]/a/text()').extract_first()
        title = response.xpath('//h3/text()').extract_first()  # 某些吧标题在h1
        if title is None:
            title = response.xpath('//h1/text()').extract_first()
        try:
            for each in response.xpath('//div[starts-with(@class,"l_post")]'):
                username = each.xpath('.//li[@class="d_name"]/a/text()').extract_first()
                pushtime = each.xpath('.//span[@class="tail-info"][3]/text()').extract_first()  # 移动端
                if pushtime is None:
                    pushtime = each.xpath('.//span[@class="tail-info"][2]/text()').extract_first()  # PC端
                # pushtime = json.loads(data)["content"]["date"]
                comtpath = each.xpath('.//div[starts-with(@id,"post_content_")]')
                comtstr = comtpath.xpath('string(.)').extract_first()
                if comtstr is None:
                    continue
                item = BaseItem()
                item['title'] = title
                item['bbs_name'] = '百度贴吧'
                item['sonbbs_name'] = bbsname
                item['username'] = username
                item['comment_detail'] = comtstr
                item['comment_url'] = response.url
                item['push_time'] = pushtime
                item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item['car_type'] = None
                item['collection'] = "百度贴吧(test)"
                item['usergender'] = None
                item['userlocation'] = None
                item['userage'] = None
                yield item

            # 发送获取回复的请求
            tid = re.search('p/(\d+)', response.url).group(1)
            pg_num = re.search('pn=(\d+)', response.url)
            total_comment_url = "https://tieba.baidu.com/p/totalComment?tid={}".format(tid)
            if pg_num:
                pg_num = pg_num.group(1)
                total_comment_url += "&pn={}".format(pg_num)
            meta = {
                "title": title,
                "sonbbs_name": bbsname,
                "comment_url": response.url
            }
            yield scrapy.Request(url=total_comment_url, callback=self.parse_comment, meta=meta)
        except Exception as e:
            self.error('【parse_detail出错】url:{}; line{}:{}'.format(response.url, e.__traceback__.tb_lineno, e))

    def parse_comment(self, response):
        # response.encoding = 'utf8'
        # print(response.text)
        try:
            data = json.loads(response.text)
            comment_list = data['data']['comment_list']
            for key in comment_list.keys():
                for comment in comment_list[key]["comment_info"]:
                    item = BaseItem()
                    item['title'] = response.meta["title"]
                    item['bbs_name'] = '百度贴吧'
                    item['sonbbs_name'] = response.meta["sonbbs_name"]
                    item['username'] = comment["username"]
                    item['comment_detail'] = comment["content"]
                    item['comment_url'] = response.meta["comment_url"]
                    pushtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment["now_time"]))
                    item['push_time'] = pushtime
                    item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    item['car_type'] = None
                    item['collection'] = "百度贴吧(test)"
                    item['usergender'] = None
                    item['userlocation'] = None
                    item['userage'] = None
                    yield item
        except Exception as e:
            self.error('【无评论】url:{}; line{}:{}'.format(response.url, e.__traceback__.tb_lineno, e))

