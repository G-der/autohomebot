import time
from datetime import date
from scrapy.spiders import CrawlSpider, Rule
import re
from scrapy.linkextractors import LinkExtractor
from autohomebot.items import BaseItem
import requests
from lxml import etree


class MotuomiSpider(CrawlSpider):
    # spider的唯一名称
    name = 'imotor'
    allowed_domains = ["www.i-motor.com.cn"]
    # 开始爬取的url
    start_urls = [
        "http://www.i-motor.com.cn/forum-402-1.html",  # 热帖推荐
        # "http://www.i-motor.com.cn/forum-69-1.html",  # 豪爵摩托
        # "http://www.i-motor.com.cn/forum-102-1.html",  # 力帆摩托
        # "http://www.i-motor.com.cn/forum-291-1.html",  # 光阳摩托
        # "http://www.i-motor.com.cn/forum-289-1.html",  # 雅马哈
    ]
    # 从页面需要提取的url 链接(link)
    forums = LinkExtractor(allow="forum-")  # 提取所有论坛链接  添加restrict_xpaths='//div[@class="pg"]'可设置只提取本论坛分页链接
    links = LinkExtractor(allow="thread-",  # 提取帖子链接
                          restrict_xpaths=['//tbody[starts-with(@id,"normalthread_")]', '//div[@class="pg"]']
                          )
    # 设置解析link的规则，callback是指解析link返回的响应数据的的方法
    rules = [
        Rule(link_extractor=forums, follow=True),
        Rule(link_extractor=links, callback="parseContent", follow=True)
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

    def parseContent(self, response):
        title = response.xpath('//span[@id="thread_subject"]/text()').extract_first()
        sonbbs_name = response.xpath('//div[@class="z"]/a[4]/text()').extract_first()
        try:
            for each in response.xpath('//div[@id="ct"]/div[@id="postlist"]/div'):
                # 获取用户名
                username = each.xpath('.//div[@class="authi"]/a[@class="xw1"]/text()').extract_first()
                if username is None:
                    continue
                urlstr = each.xpath('.//div[@class="authi"]/a[@class="xw1"]/@href').extract_first()
                uid = re.search('\d+',urlstr).group()
                userurl = 'http://www.i-motor.com.cn/home.php?mod=space&uid={}&do=profile'.format(uid)
                usermsg = self.parse_user(userurl)
                # 获取评论详情
                comt_path = each.xpath('.//td[@class="t_f"]')
                comt = comt_path.xpath('string(.)').extract_first()
                # 获取论坛url
                comturl = response.url
                # 获取评论时间
                pushtime = each.xpath('.//div[@class="authi"]/em/text()').extract_first()

                item = BaseItem()
                item['title'] = title
                item['bbs_name'] = 'imotor'
                item['sonbbs_name'] = sonbbs_name
                item['username'] = username
                item['comment_detail'] = comt
                item['comment_url'] = comturl
                item['push_time'] = pushtime
                item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item['car_type'] = None
                item['collection'] = "imotor"
                item['usergender'] = usermsg[0]
                item['userlocation'] = usermsg[1]
                item['userage'] = usermsg[2]
                yield item
        except Exception as e:
            self.error('【parse_detail出错】url:{}; line{}:{}'.format(response.url, e.__traceback__.tb_lineno, e))

    def parse_user(self, url):
        response = etree.HTML(requests.get(url).text)
        usermsg = []
        # 性别
        usergender = response.xpath('//ul[@class="pf_l cl"]//em[contains(text(),"性别")]/../text()')
        if usergender:
            usergender = usergender[0]
        else:
            usergender = None
        usermsg.append(usergender)

        # 所在地
        userlocation = response.xpath('//ul[@class="pf_l cl"]//em[contains(text(),"居住地")]/../text()')
        if userlocation:
            userlocation = userlocation[0]
        else:
            userlocation = None
        usermsg.append(userlocation)

        # 年龄
        userbirthday = response.xpath('//ul[@class="pf_l cl"]//em[contains(text(),"生日")]/../text()')
        if userbirthday:
            try:
                userbirthday = userbirthday[0]
                birthyear = int(re.match('\d+', userbirthday).group())
                age = str(date.today().year - birthyear)
                usermsg.append(age)
            except:
                usermsg.append(None)
        else:
            usermsg.append(None)
        return usermsg
