import re
import time
import scrapy
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from autohomebot.items import BaseItem


class NiumoKBSpider(CrawlSpider):
    name = 'niumoKB'
    allowed_domains = ['www.newmotor.com.cn', 'motor.newmotor.com.cn']
    start_urls = [
        # "http://www.newmotor.com.cn/sale/?0-0-0-0-0-0-0-0-0-0-0-1",  # 车型列表首页
        "http://motor.newmotor.com.cn/GZ150A135/koubei.shtml",  # 豪爵铃木 悦酷GZ150
        'http://motor.newmotor.com.cn/LF15010B249/koubei.shtml',  # 力帆 KP150
        'http://motor.newmotor.com.cn/zy125t136963/koubei.shtml',  # 雅马哈 巧格i
        'http://motor.newmotor.com.cn/CK110T3Bdianpenban5951/koubei.shtml',  # 光阳 劲丽110Fi
        'http://motor.newmotor.com.cn/UU125i7185/koubei.shtml',  # 济南铃木 优友125
        'http://motor.newmotor.com.cn/ZY125T96033/koubei.shtml',  # 雅马哈 尚领125
    ]
    # PGlinks = LinkExtractor(allow="\?0-0-0-0-0-0-0-0-0-0-0-\d+", restrict_xpaths='//p[@class="tw_gmpage"]')  # 车型列表翻页
    # KBlinks = LinkExtractor(allow="koubei", restrict_xpaths='//div[@class="more"]')  # 车型口碑首页
    pllinks = LinkExtractor(allow=('haoping', 'chaping'),restrict_xpaths='//ul[@class="comment_tab clearfix"]')  # 好评和差评链接提取规则
    rules = [
        # Rule(link_extractor=PGlinks, follow=True),
        # Rule(link_extractor=KBlinks, follow=True),
        Rule(link_extractor=pllinks, callback='parse_content', follow=True)
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
        # self.info('牛摩网:[{}]、.状态:[{}]'.format(response.url, response.status))
        title_path = response.xpath('//h1')
        title = title_path.xpath("string(.)").extract_first()
        try:
            for each in response.xpath('//ul[@class="comment_list"]/li'):
                item = BaseItem()
                commenturl = response.url
                username = each.xpath('.//p/text()').extract_first()
                commentdetail = each.xpath('.//dd/text()').extract_first()
                pushtime = each.xpath('./div/div/div/text()').extract_first()

                item['title'] = title + "评论"
                item['bbs_name'] = '牛摩论坛'
                item['sonbbs_name'] = None
                item['username'] = username
                if item['username'] is None:
                    continue
                item['comment_detail'] = commentdetail
                # if not isinstance(item['comment_detail'], str):
                #     continue
                item['comment_url'] = commenturl
                item['push_time'] = pushtime
                item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item['car_type'] = title
                item['collection'] = "牛摩网(竞品)"  # TODO 修改表名
                item['usergender'] = None
                item['userlocation'] = None
                item['userage'] = None
                yield item
        except Exception as e:
            self.error('【parse_detail出错】url:{}; line{}:{}'.format(response.url, e.__traceback__.tb_lineno, e))


