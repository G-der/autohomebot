import time
from datetime import datetime
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from autohomebot.items import ArticleItem


class WyzxSpider(CrawlSpider):
    name = "wyzxwk"
    start_urls = [
        # "http://www.wyzxwk.com/article/ualist/index.html",  # 最新文章
        # "http://www.wyzxwk.com/article/center/index.html",  # 文章导航
        "http://www.wyzxwk.com/Article/shidai",
        'http://www.wyzxwk.com/Article/yulun',
        'http://www.wyzxwk.com/Article/jingji',
        'http://www.wyzxwk.com/Article/shehui',
        'http://www.wyzxwk.com/Article/sannong',
        'http://www.wyzxwk.com/Article/chanye',
        'http://www.wyzxwk.com/Article/guoji',
        'http://www.wyzxwk.com/Article/guofang',
        'http://www.wyzxwk.com/Article/lixiang',
        'http://www.wyzxwk.com/Article/sichao',
        'http://www.wyzxwk.com/Article/wenyi',
        'http://www.wyzxwk.com/Article/shushe',
        'http://www.wyzxwk.com/Article/lishi',
        'http://www.wyzxwk.com/Article/zhonghua',
        'http://www.wyzxwk.com/Article/zhongyi',
        'http://www.wyzxwk.com/Article/cpers',
        'http://www.wyzxwk.com/Article/qingnian',
        'http://www.wyzxwk.com/Article/gongnong',
        'http://www.wyzxwk.com/Article/zatan',
        'http://www.wyzxwk.com/Article/shiping'
        ]

    # section_links = LinkExtractor(allow="Article", restrict_xpaths='//div[@class="g-sd-nav s-shadow"]')
    list_links = LinkExtractor(allow="index", restrict_xpaths='//div[@class="m-pages"]')
    art_links = LinkExtractor(allow=r"\d+", restrict_xpaths='//div[@class="m-pt s-h130" or @class="m-pt s-h120"]', deny="tags")

    rules = [
        Rule(list_links, follow=True),
        Rule(art_links, callback='parse_art'),
        # Rule(section_links, follow=False),
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

    def parse_art(self, response):
        time_str = response.xpath('//div[@class="f-fl"]/span[3]/text()').extract_first()
        push_time = datetime.strptime(time_str, "%Y-%m-%d")  # 字符串化为时间
        start_time = datetime.strptime('2018-03-01', "%Y-%m-%d")  # 字符串化为时间
        if push_time >= start_time:
            try:
                item = ArticleItem()
                item["title"] = response.xpath('//h1/text()').extract_first().strip()
                item["author"] = response.xpath('//div[@class="f-fl"]/span[1]/text()').extract_first()
                item["push_time"] = time_str
                source = response.xpath('//div[@class="f-fl"]/text()[6]').extract_first().strip()
                item["source"] = source
                art_path = response.xpath('//article')
                item["url"] = response.url
                item["detail"] = art_path.xpath('string(.)').extract_first().strip()
                item['catch_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item['collection'] = "乌有之乡网刊(2018/3)"
                item['type'] = response.xpath('//span[@class="s-last"]/a/text()').extract_first()
                yield item
            except Exception as e:
                print("解析失败", e.__traceback__.tb_lineno, e)
