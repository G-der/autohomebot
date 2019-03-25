from datetime import date
import random
import requests
from lxml import etree
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import re
import time
from autohomebot.items import BaseItem


class AutoHomeBBS(CrawlSpider):
    name = 'qczj'
    # allowed_domains = ["club.autohome.com.cn"]
    start_urls = [
        # "https://club.autohome.com.cn/bbs/forum-o-200063-1.html",  # 摩托车论坛
        # "https://club.autohome.com.cn/bbs/forum-o-210063-1.html",  # 宝马
        # "https://club.autohome.com.cn/bbs/forum-o-210163-1.html",  # 哈雷
        # "https://club.autohome.com.cn/bbs/forum-o-210263-1.html",  # 杜卡迪
        # "https://club.autohome.com.cn/bbs/forum-o-210363-1.html",  # 贝纳利
        # "https://club.autohome.com.cn/bbs/forum-o-210463-1.html",  # 铃木
        # "https://club.autohome.com.cn/bbs/forum-o-210563-1.html",  # 雅马哈
        # "https://club.autohome.com.cn/bbs/forum-o-210663-1.html",  # KTM
        # "https://club.autohome.com.cn/bbs/forum-o-210763-1.html",  # 本田
        'https://club.autohome.com.cn/bbs/forum-o-210763-1.html?qaType=-1#pvareaid=101061'
        # "https://club.autohome.com.cn/bbs/forum-o-210863-1.html",  # 春风
        # "https://club.autohome.com.cn/bbs/forum-o-210963-1.html"   # 川崎
    ]
    pages = LinkExtractor(allow="/bbs/forum-o-",
                          restrict_xpaths=['//div[@class="pagearea"]'])
    links = LinkExtractor(allow="/bbs/thread",
                          restrict_xpaths=['//div[@id="subcontent"]', '//div[@class="pages"]']
                          )
    rules = [
        Rule(link_extractor=pages, follow=True),
        Rule(link_extractor=links, callback="parseAutoBBS", follow=True)
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

    def parseAutoBBS(self, response):
        try:
            item = BaseItem()
            # TODO 检测是否被重定向，若爬其他论坛需修改此处
            html = str(response.body)
            if "本田摩托车论坛" not in html:
                item['comment_url'] = response.url
                item['collection'] = "test"
                yield item
                return
            title = response.xpath('//div[@id="consnav"]/span[4]/text()').extract_first()
            bbsname = response.xpath('//div[@id="consnav"]/span[2]/a/text()').extract_first()
            for each in response.xpath('//div[@id="maxwrap-reply"]/div[@class="clearfix contstxt outer-section"]'):
                username = each.xpath('.//li[@class="txtcenter fw"]/a/text()').extract_first().strip()
                # userloc = each.xpath('.//ul[@class="leftlist"]/li[6]/a/text()').extract_first()
                uid = each.xpath('./@uid').extract_first()
                userurl = "https://i.autohome.com.cn/{}/info".format(uid)
                usermsg = self.parse_user(userurl)
                pushtime = each.xpath('.//span[@xname="date"]/text()').extract_first()
                comtpath = each.xpath('.//div[@class="x-reply font14"]')
                comtstr = comtpath.xpath('string(.)').extract_first().strip()

                item['title'] = title
                item['bbs_name'] = '汽车之家'
                item['sonbbs_name'] = bbsname
                item['username'] = username
                item['comment_detail'] = comtstr
                item['comment_url'] = response.url
                item['push_time'] = pushtime
                item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item['car_type'] = None
                item['collection'] = "汽车之家(test)"
                item['usergender'] = usermsg[0]
                item['userlocation'] = usermsg[1]
                item['userage'] = usermsg[2]
                yield item
        except Exception as e:
            self.error('【parse_detail出错】url:{}; line{}:{}'.format(response.url, e.__traceback__.tb_lineno, e))

    def parse_user(self, url):
        ramdom = random.randint(1, 3)
        time.sleep(0.5*ramdom)
        headers = {
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,ja-JP;q=0.5',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Cookie': '__ah_uuid=5A18FE88-92EC-4533-86BA-1A7611836272; fvlid=155194434812913W8OrH8Il; sessionip=121.15.166.89; sessionid=8680C623-DB64-463D-A471-C0392E621CB5%7C%7C2019-03-07+15%3A39%3A10.443%7C%7Cwww.baidu.com; area=440303; ahpau=1; pbcpopclub=3fffbd5a-fa98-49ff-9aeb-149212bc161d; sessionuid=8680C623-DB64-463D-A471-C0392E621CB5%7C%7C2019-03-07+15%3A39%3A10.443%7C%7Cwww.baidu.com; historybbsName4=o-200063%7C%E6%91%A9%E6%89%98%E8%BD%A6%2Co-210063%7C%E5%AE%9D%E9%A9%AC%E6%91%A9%E6%89%98%E8%BD%A6%2Co-210163%7C%E5%93%88%E9%9B%B7%E6%91%A9%E6%89%98%E8%BD%A6%2Co-210263%7C%E6%9D%9C%E5%8D%A1%E8%BF%AA%E6%91%A9%E6%89%98%E8%BD%A6%2Co-210363%7C%E8%B4%9D%E7%BA%B3%E5%88%A9%E6%91%A9%E6%89%98%E8%BD%A6%2Co-210463%7C%E9%93%83%E6%9C%A8%E6%91%A9%E6%89%98%E8%BD%A6%2Co-210563%7C%E9%9B%85%E9%A9%AC%E5%93%88%E6%91%A9%E6%89%98%E8%BD%A6%2Cc-606%7CV3%E8%8F%B1%E6%82%A6%2Cc-2123%7C%E5%93%88%E5%BC%97H6%2Cc-2733%7C%E5%A5%A5%E8%BF%AARS; pvidlist=57f72644-837b-40ea-aee3-4e3fed2f3d7722:246745:383226:0:1:1509263; tuanpvareaid=6828690; tuan_subject47_onceorder=ON; tuan_access_id=3363d8b59de24bfb9be71b439bcfe69f; autoac=F655D9BAFED30C7200ADB0CA20D78E40; autotc=7D04798754D68D6C1F87BA3B4E08DF6A; pvidchain=2199101; sessionvid=19C87C53-66B5-4FD4-9DDB-3E234D3AA010; __utma=1.468985631.1552276351.1552276351.1552276351.1; __utmb=1.0.10.1552276351; __utmc=1; __utmz=1.1552276351.1.1.utmcsr=i.autohome.com.cn|utmccn=(referral)|utmcmd=referral|utmcct=/646010; pcpopclub=03f34dc6600a475cabd914deb21b0d2f05b86483; clubUserShow=95970435|66|6|afq79a|0|0|0||2019-03-11 11:54:14|0; autouserid=95970435; sessionuserid=95970435; ahpvno=53; sessionlogin=3bd6d4b239b84aee9fea70daa091cb2b05b86483; ASP.NET_SessionId=b25tiqwyxn0cy14x1r3jk43o; ref=www.baidu.com%7C0%7C0%7Cblog.csdn.net%7C2019-03-11+11%3A54%3A22.863%7C2019-03-11+10%3A42%3A36.563; ahrlid=1552276459850J7aQ3KTQNR-1552276497526'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            html = etree.HTML(response.text)
            usermsg = []
            # 性别
            usergender = html.xpath('//span[contains(text(),"性别")]/../text()[2]')
            if usergender is not None:
                try:
                    usergender = usergender[0]
                except:
                    usergender = None
            usermsg.append(usergender)

            # 所在地
            userlocation = html.xpath('//span[contains(text(),"所在地")]/../text()[2]')
            if userlocation is not None:
                try:
                    userlocation = userlocation[0]
                except:
                    userlocation = None
            usermsg.append(userlocation)

            # 年龄
            userbirthday = html.xpath('//span[contains(text(),"生日")]/../text()[2]')
            if userbirthday is not None:
                try:
                    userbirthday = userbirthday[0]
                    birthyear = int(re.match('\d+', userbirthday).group())
                    age = str(date.today().year - birthyear)
                    usermsg.append(age)
                except:
                    usermsg.append(None)
            else:
                usermsg.append(None)
        else:
            self.info("获取用户信息失败")
            usermsg = [None, None, None]
        return usermsg
