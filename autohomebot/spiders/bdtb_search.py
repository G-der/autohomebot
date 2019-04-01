import json
from datetime import datetime
from scrapy.spiders import Spider
import scrapy
import re
import time
from autohomebot.items import BaseItem


class BaiDuTieBaSearch(Spider):
    start_time = "2018-01-01"
    name = 'baidusearch'
    # allowed_domains = ""
    kw = '中日龙 -棒球 -中日龙队 -大阪 -球迷 -中日龙路 -襄阳 -职棒'  # 丰田合成（佛山）橡塑  上海大道包装隔热材料 阿尔发(广州)汽车配件
    base_kw = "中日龙"
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
        base_url = "http://tieba.baidu.com"
        for item in response.xpath('//div[@class="s_post"]'):
            url = item.xpath('./span/a/@href').extract_first()
            easy_url = url.split("?", 1)[0]
            pid = re.search(r"pid=(\d+)", url.split("?", 1)[1]).group(1)
            pushtime = item.xpath('.//font[@class="p_green p_date"]/text()').extract_first()
            if pushtime < self.start_time:
                return
            full_url = base_url + easy_url
            meta = {"pid": pid}
            yield scrapy.Request(url=full_url,callback=self.parse_tiezi,meta=meta)
        next_pg = response.xpath('//a[text()="下一页>"]/@href')
        if next_pg:
            next_url = base_url + next_pg.extract_first()
            yield scrapy.Request(url=next_url, callback=self.parse)

    def parse_tiezi(self,response):
        bbsname = response.xpath('//div[@class="card_title "]/a/text()').extract_first()
        title = response.xpath('//h3/text()').extract_first()  # 某些吧标题在h1
        if title is None:
            title = response.xpath('//h1/text()').extract_first()
        try:
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
            # yield scrapy.Request(url=total_comment_url, callback=self.parse_comment, meta=meta)
            # 3.27若非主题帖,则只爬取当前回复贴
            if self.base_kw not in title:
                base_path = response.xpath('//div[@id="post_content_{}"]/../../../..'.format(response.meta["pid"]))

                # 处理帖子评论
                reply_num = 0
                try:
                    data = base_path.xpath('./@data-field').extract_first()
                    reply_num = int(json.loads(data)["content"]["comment_num"])
                except:
                    print("获取评论数出错")
                    pass
                # reply_str = base_path.xpath('.//a[@class="lzl_link_unfold" or @class="p_reply_first"]/text()').extract_first()
                # reply_num = re.search(r"\d+", reply_str)
                if reply_num is not 0:
                    meta["pid"] = response.meta["pid"]
                    yield scrapy.Request(url=total_comment_url, callback=self.parse_comment, meta=meta)

                username = base_path.xpath('.//li[@class="d_name"]/a/text()').extract_first()
                pushtime = base_path.xpath('.//span[@class="tail-info"][3]/text()').extract_first()  # 移动端
                if pushtime is None:
                    pushtime = base_path.xpath('.//span[@class="tail-info"][2]/text()').extract_first()  # PC端
                if pushtime is None:
                    try:
                        data = base_path.xpath('./@data-field').extract_first()
                        pushtime = json.loads(data)["content"]["date"]
                    except:
                        return
                if pushtime < self.start_time:  # 3.26添加时间条件
                    return
                comtpath = base_path.xpath('.//div[starts-with(@id,"post_content_")]')
                comtstr = comtpath.xpath('string(.)').extract_first()
                if comtstr is None:
                    return
                item = BaseItem()
                item['title'] = title
                item['bbs_name'] = '百度贴吧'
                item['sonbbs_name'] = bbsname
                item['username'] = username
                item['comment_detail'] = comtstr
                item['comment_url'] = response.url
                item['push_time'] = pushtime
                if pushtime < self.start_time:  # 3.26添加时间条件
                    return
                item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item['car_type'] = None
                item['collection'] = "百度贴吧搜索({})".format(self.kw)
                item['usergender'] = None
                item['userlocation'] = None
                item['userage'] = None
                yield item
                return 

            else:
                yield scrapy.Request(url=total_comment_url, callback=self.parse_comment, meta=meta)
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
                    if pushtime < self.start_time:  # 3.26添加时间条件
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
                    if pushtime < self.start_time:  # 3.26添加时间条件
                        continue
                    item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    item['car_type'] = None
                    item['collection'] = "百度贴吧搜索({})".format(self.kw)
                    item['usergender'] = None
                    item['userlocation'] = None
                    item['userage'] = None
                    yield item

        except Exception as e:
            self.error('【parse_detail出错】url:{}; line{}:{}'.format(response.url, e.__traceback__.tb_lineno, e))

    def parse_comment(self, response):
        # response.encoding = 'utf8'
        # print(response.text)
        try:
            data = json.loads(response.text)
            comment_list = data['data']['comment_list']
            pid = response.meta.get("pid")
            # 只获取指定帖子的评论
            if pid:
                for comment in comment_list[pid]["comment_info"]:
                    item = BaseItem()
                    item['title'] = response.meta["title"]
                    item['bbs_name'] = '百度贴吧'
                    item['sonbbs_name'] = response.meta["sonbbs_name"]
                    item['username'] = comment["username"]
                    item['comment_detail'] = comment["content"]
                    item['comment_url'] = response.meta["comment_url"]
                    pushtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(comment["now_time"]))
                    if pushtime < self.start_time:  # 3.26添加时间条件
                        continue
                    item['push_time'] = pushtime
                    item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    item['car_type'] = None
                    item['collection'] = "百度贴吧搜索({})".format(self.kw)
                    item['usergender'] = None
                    item['userlocation'] = None
                    item['userage'] = None
                    yield item
            # 获取全部评论
            else:
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
                        if pushtime < self.start_time:  # 3.26添加时间条件
                            continue
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
