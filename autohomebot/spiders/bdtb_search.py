import json
from datetime import datetime
from scrapy.spiders import Spider
import scrapy
import re
import time
from autohomebot.items import BaseItem


class BaiDuTieBaSearch(Spider):
    name = 'baidusearch'
    # allowed_domains = ""
    kw = '三樱汽车部件+东莞'  # 丰田合成（佛山）橡塑  上海大道包装隔热材料 阿尔发(广州)汽车配件
    start_urls = ["http://tieba.baidu.com/f/search/res?qw={}&ie=utf-8".format(kw)]

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

    def parse(self, response):
        for item in response.xpath('//div[@class="s_post"]'):
            url = item.xpath('./span/a/@href').extract_first()
            p_num = re.search(r'p/(\d+)', url).group(1)
            base_url = "http://tieba.baidu.com"
            full_url = base_url +url
            yield scrapy.Request(url=full_url,callback=self.parse_tiezi)
        next_pg = response.xpath('//a[text()="下一页>"]/@href')
        if next_pg:
            next_url = base_url + next_pg.extract_first()
            yield scrapy.Request(url=next_url,callback=self.parse)

    def parse_tiezi(self,response):
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
                if pushtime is None:
                    try:
                        data = each.xpath('./@data-field').extract_first()
                        pushtime = json.loads(data)["content"]["date"]
                    except:
                        continue
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
                item['collection'] = "百度贴吧搜索({})".format(self.kw)
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
                    item['collection'] = "百度贴吧搜索({})".format(self.kw)
                    item['usergender'] = None
                    item['userlocation'] = None
                    item['userage'] = None
                    yield item
        except Exception as e:
            self.error('【无评论】url:{}; line{}:{}'.format(response.url, e.__traceback__.tb_lineno, e))
