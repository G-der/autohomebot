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
    name = 'mtm'
    allowed_domains = ["motorcycle.sh.cn"]
    # 开始爬取的url
    start_urls = [
        # "http://motorcycle.sh.cn/forum.php?gid=3",  # 摩托车论坛
        # "http://motorcycle.sh.cn/forum.php?gid=171",  # 摩托车整车厂家专区
        "http://motorcycle.sh.cn/forum.php?gid=17",  # 各地摩托车友交流区
        "http://motorcycle.sh.cn/forum-102-1.html",  # 五羊本田骑式车讨论区
        "http://motorcycle.sh.cn/forum-144-1.html",  # 五羊本田-踏板车讨论专区
        "http://motorcycle.sh.cn/forum-113-1.html",  # 五羊本田-弯梁车讨论专区
    ]

    # 从页面需要提取的url 链接(link)
    forums = LinkExtractor(allow="forum-",
                           restrict_xpaths=['//table[@class="fl_tb"]', '//div[@class="pg"]'])  # restrict_xpaths='//div[@class="pg"]'，
    links = LinkExtractor(allow="thread-",
                          restrict_xpaths=['//tbody[starts-with(@id,"normalthread_")]', '//div[@class="pg"]'],)

    # 设置解析link的规则，callback是指解析link返回的响应数据的的方法
    rules = [
        Rule(link_extractor=links, callback="parseContent", follow=True),
        Rule(link_extractor=forums, follow=True)
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
        """
        解析响应的数据，获取需要的数据字段
        :param response: 响应的数据
        :return:
        """
        title = response.xpath('//span[@id="thread_subject"]/text()').extract_first()
        sonbbs_name = response.xpath('//div[@class="z"]/a[4]/text()').extract_first()
        try:
            for each in response.xpath('//div[@id="ct"]/div[@id="postlist"]/div'):
                # 获取用户名
                username = each.xpath('.//div[@class="authi"]/a[@class="xw1"]/text()').extract_first()
                if username is None:
                    continue
                userurl = 'http://motorcycle.sh.cn/' + each.xpath(
                    './/div[@class="authi"]/a[@class="xw1"]/@href').extract_first()
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
                item['bbs_name'] = '摩托迷'
                item['sonbbs_name'] = sonbbs_name
                item['username'] = username
                item['comment_detail'] = comt
                item['comment_url'] = comturl
                item['push_time'] = pushtime
                item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item['car_type'] = None
                item['collection'] = "摩托迷(3.22)"
                item['usergender'] = usermsg[0]
                item['userlocation'] = usermsg[1]
                if item['userlocation'] is None and "摩友交流区" in sonbbs_name:
                    item['userlocation'] = sonbbs_name.replace("摩友交流区",'')
                item['userage'] = usermsg[2]
                yield item
        except Exception as e:
            self.error('【parse_detail出错】url:{}; line{}:{}'.format(response.url, e.__traceback__.tb_lineno, e))

    def parse_user(self, url):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
        }
        api_url = 'http://127.0.0.1:5555/random'  # API接口
        r = requests.get(api_url, timeout=8)
        proxies = {
            'https': "https://" + r.text
        }
        response = requests.get(url, headers=headers, proxies=proxies)
        if response.status_code == 200:
            html = etree.HTML(response.text)
            usermsg = []
            # 性别
            usergender = html.xpath('//ul[@class="pf_l cl"]//em[contains(text(),"性别")]/../text()')
            if usergender:
                usergender = usergender[0]
            else:
                usergender = None
            usermsg.append(usergender)

            # 所在地
            userlocation = html.xpath('//ul[@class="pf_l cl"]//em[contains(text(),"居住地")]/../text()')
            if userlocation:
                userlocation = userlocation[0]
            else:
                userlocation = None
            usermsg.append(userlocation)

            # 年龄
            userbirthday = html.xpath('//ul[@class="pf_l cl"]//em[contains(text(),"生日")]/../text()')
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
        else:
            return [None, None, None]
