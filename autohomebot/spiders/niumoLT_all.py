import re
import time
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from autohomebot.items import BaseItem


class niumoLT(CrawlSpider):
    name = "nmlt"
    allowed_domains = ['bbs.newmotor.com.cn']
    start_urls = [
        # "http://bbs.newmotor.com.cn/",  # 论坛首页开始,提取全站
        "http://bbs.newmotor.com.cn/index.shtml?page=1&boardid=93",  # 豪爵铃木
        "http://bbs.newmotor.com.cn/index.shtml?page=1&boardid=92",  # 力帆
        "http://bbs.newmotor.com.cn/index.shtml?page=1&boardid=119",  # 光阳
        "http://bbs.newmotor.com.cn/index.shtml?page=1&boardid=129",  # 建设雅马哈
        "http://bbs.newmotor.com.cn/index.shtml?page=1&boardid=197",  # 雅马哈
        "http://bbs.newmotor.com.cn/index.shtml?page=1&boardid=128"  # 轻骑铃木
    ]
    # LTlinks = LinkExtractor(allow='index\.shtml.boardid=\d+')  # 论坛链接提取规则
    LTPlinks = LinkExtractor(allow='boardid=', restrict_xpaths='//div[@id="fenye"]')  # 论坛分页链接提取规则
    TZlinks = LinkExtractor(allow='display',
                            restrict_xpaths=['//div[@id="fenye"]', '//table[@class="topiclist"]'],  # 帖子和帖子分页链接提取规则
                            deny=['38357', '85179'])  # 过滤置顶帖
    rules = [
        # Rule(link_extractor=LTlinks, follow=True),
        Rule(link_extractor=LTPlinks, follow=True),
        Rule(link_extractor=TZlinks, callback='parse_content', follow=True)
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

    def parse_content(self, response):
        """解析页面"""
        # self.info('牛摩网:[{}]、.状态:[{}]'.format(response.url, response.status))
        sonbbs_name = response.xpath('//div[@class="navigations"]/a[4]/text()').extract_first()
        if sonbbs_name is None:
            sonbbs_name = response.xpath('//div[@class="navigations"]/a[3]/text()').extract_first()
        title = response.xpath('//p[@style="position:relative;"]/text()').extract_first()
        try:
            for each in response.xpath('//div[@id="club_content_list"]'):
                commenturl = response.url
                username = each.xpath('.//strong/text()').extract_first()
                pushtime_str = each.xpath('.//span[@style="float:left"]/text()').extract_first()
                # 处理时间
                try:
                    pushtime = pushtime_str.replace(' 发表于：', '')
                    if re.search("昨天", pushtime):
                        yestoday = time.strftime("%Y/%m/%d", time.localtime(time.time() - 86400))
                        pushtime = pushtime.replace('昨天', yestoday)
                    if re.search('前天', pushtime):
                        Byestoday = time.strftime("%Y/%m/%d", time.localtime(time.time() - 172800))
                        pushtime = pushtime.replace('前天', Byestoday)
                    if re.search('今天', pushtime):
                        Byestoday = time.strftime("%Y/%m/%d", time.localtime(time.time()))
                        pushtime = pushtime.replace('今天', Byestoday)
                    if re.search('小时前', pushtime):
                        NUM = int(re.search('\d+', pushtime).group())
                        sec = NUM * 60 * 60
                        today = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time() - sec))
                        pushtime = pushtime.replace("{} 小时前".format(NUM), today)
                    if re.search('分钟前', pushtime):
                        NUM = int(re.search('\d+', pushtime).group())
                        sec = NUM * 60
                        today = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime(time.time() - sec))
                        pushtime = pushtime.replace("{} 分钟前".format(NUM), today)
                except:
                    continue

                # 若无文字，抛弃此对象
                comtstr = None
                try:
                    comt = each.xpath('.//div[@class="clubcontent"]/node()').extract()
                    # 获取并清洗帖子内容
                    comtstr = ''.join(comt)
                    rush = ['\r', '<.*?>', '\xa0', '\n']
                    for item in rush:
                        comtstr = re.sub(item, '', comtstr)
                except:
                    pass
                item = BaseItem()
                item['title'] = title
                item['bbs_name'] = '牛摩论坛'
                item['sonbbs_name'] = sonbbs_name
                item['username'] = username
                if item['username'] is None:
                    continue
                item['comment_detail'] = comtstr
                if not isinstance(item['comment_detail'], str):
                    continue
                item['comment_url'] = commenturl
                item['push_time'] = pushtime
                item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item['car_type'] = None
                item['collection'] = "牛摩网(竞品)"  # TODO 修改表名
                item['usergender'] = None
                item['userlocation'] = None
                item['userage'] = None
                yield item
        except Exception as e:
            self.error('【parse_detail出错】{},{}'.format(response.url, e))
