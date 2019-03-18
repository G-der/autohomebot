import csv
import scrapy
from scrapy import Request
import re
import pandas
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider,Rule
from autohomebot.items import urlitems


class niumoLT(CrawlSpider):
    name = "nmlturl"
    allowed_domains = ['bbs.newmotor.com.cn']
    start_urls = ["http://bbs.newmotor.com.cn/"]
    LTlinks = LinkExtractor(allow='index\.shtml.boardid=\d+')
    # LTPlinks = LinkExtractor(allow='page=\d+&boardid=\d+')
    # TZlinks = LinkExtractor(allow='display.shtml')
    rules = [
        # Rule(link_extractor=LTlinks, follow=True),
        # Rule(link_extractor=LTPlinks, follow=True),
        Rule(link_extractor=LTlinks, callback='parse_Links')
    ]

    def parse_Links(self, response):
        item = urlitems()
        url = response.url
        sonbbs_name = response.xpath('//div[@class="navigations"]/a[4]/text()').extract_first()
        if sonbbs_name is None:
            sonbbs_name = response.xpath('//div[@class="navigations"]/a[3]/text()').extract_first()
        item["url"] = url
        item["name"] = sonbbs_name
        item["collection"] = 'niumoLTurl'
        yield item




