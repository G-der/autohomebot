from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
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
        "https://tieba.baidu.com/f?kw=%D4%C3%BF%E1",  # 悦酷吧
        "https://tieba.baidu.com/f?ie=utf-8&kw=力帆kp150",  # 力帆kp150吧
        "https://tieba.baidu.com/f?ie=utf-8&kw=雅马哈巧格i",  # 雅马哈巧格i吧
        "https://tieba.baidu.com/f?ie=utf-8&kw=光阳劲丽",  # 光阳劲丽吧
        "https://tieba.baidu.com/f?ie=utf-8&kw=铃木优友",  # 铃木优友吧
        "https://tieba.baidu.com/f?ie=utf-8&kw=雅马哈尚领",  # 雅马哈尚领吧
        # "https://tieba.baidu.com/p/6007854555"
    ]

    pages = LinkExtractor(allow="pn=", restrict_xpaths='//div[@id="frs_list_pager"]')
    links = LinkExtractor(allow="/p/\d+", deny='see_lz=1',
                          restrict_xpaths=('//ul[@id="thread_list"]', '//ul[@class="l_posts_num"]'))

    rules = [
        Rule(pages, follow=True),
        Rule(links, callback="parse_comment", follow=True)
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

    def parse_comment(self, response):
        bbsname = response.xpath('//div[@class="card_title "]/a/text()').extract_first()
        title = response.xpath('//h3/text()').extract_first()  # 某些吧标题在h1
        if title is None:
            title = response.xpath('//h1/text()').extract_first()
        try:
            for each in response.xpath('//div[starts-with(@class,"l_post")]'):
                username = each.xpath('.//img[@username]/@username').extract_first()
                if username is None:
                    username = each.xpath('.//li[@class="d_name"]/a/text()').extract_first()
                pushtime = each.xpath('.//span[@class="tail-info"][3]/text()').extract_first()  # 小吧
                if pushtime is None:
                    pushtime = each.xpath('.//span[@class="tail-info"][2]/text()').extract_first()
                # pushtime = json.loads(data)["content"]["date"]
                comtpath = each.xpath('.//div[starts-with(@id,"post_content_")]')
                comtstr = comtpath.xpath('string(.)').extract_first()

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
                item['collection'] = "百度贴吧(竞品)"
                item['usergender'] = None
                item['userlocation'] = None
                item['userage'] = None
                yield item
        except Exception as e:
            self.error('【parse_detail出错】url:{}; line{}:{}'.format(response.url, e.__traceback__.tb_lineno, e))

        # 处理回复
        # data = each.xpath('./@data-field').extract_first()
        # comment_count = json.loads(data)["content"]["comment_num"]
        # if comment_count is not 0:
        #     comment_path = each.xpath('.//div[@class="core_reply j_lzl_wrapper"]/div[2]')  # //li[starts-with(@class,"lzl_single_post")]
        #     for i in comment_path:
        #         username = i.xpath('.//a[@class="at j_user_card"]/text()').extract_first()
        #         comment = i.xpath('.//span[@class="lzl_content_main"]/text()').extract_first()
        #         pushtime = i.xpath('.//span[@class="lzl_time"]/text()').extract_first()
        #
        #         item = NiumoKBItem()
        #         item['title'] = title
        #         item['collection'] = '百度贴吧(竞品)'  # TODO 换板块时修改集合名
        #         item['username'] = username
        #         item['usergender'] = None
        #         item['userlocation'] = None
        #         item['comment_detail'] = comment
        #         item['comment_url'] = response.url
        #         item['push_time'] = pushtime
        #         item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        #         item['car_type'] = None
        #         item['data_from'] = bbsname
        #         yield item
