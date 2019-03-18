import time
import scrapy
from autohomebot.items import PcautoItem


class PcautoSpider(scrapy.Spider):
    name = 'pcauto'
    allowed_domains = ['price.pcauto.com.cn']
    start_urls = [
        'https://price.pcauto.com.cn/comment/sg90/'
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

    # 　获取评论详情
    def parse(self, response):

        self.info('太平洋汽车网:[{}]、.状态:[{}]'.format(response.url, response.status))
        title = response.xpath('//h1/text()').extract_first()
        try:
            if response.xpath('//*[@class="next"]'):
                next_page = response.xpath('//*[@class="next"]/@href').extract_first()
                next_url = "https:" + next_page
                yield scrapy.Request(next_url,callback=self.parse)
                # print(next_url)
            for each in response.xpath('//*[@class="litDy clearfix"]'):
                item = PcautoItem()
                username = each.xpath('.//*[@class="txline"]/p/a/text()').extract_first()
                pushtime = each.xpath('.//*[@class="txline"]/span/a/text()').extract_first()
                car_type = each.xpath('.//*[@class="line"][1]/a/text()').extract_first()
                buy_time = each.xpath('.//*[@class="line" and em[contains(text(),"购买时间")]]/text()').extract_first()
                buy_loca = each.xpath('.//*[@class="line" and em[contains(text(),"购买地点")]]/text()').extract_first()
                buy_shop = each.xpath('.//*[@class="line" and em[contains(text(),"购买商家")]]/text()').extract_first()
                buy_cost = each.xpath('.//*[@class="line" and em[contains(text(),"裸车价格")]]/i/text()').extract_first()
                oil_cost = each.xpath('.//*[@class="line" and em[contains(text(),"平均油耗")]]/i/text()').extract_first()
                mileage_ = each.xpath('.//*[@class="line" and em[contains(text(),"行驶里程")]]/text()').extract_first()
                buyimage = each.xpath('.//*[@class="toptit clearfix"]/a/text()').extract()
                cmt_detl = each.xpath('.//*[@class="dianPing clearfix"]')
                comment_detail = {}
                if cmt_detl:
                    comment_detail["优点"] = cmt_detl.xpath('./div[b[contains(text(),"优点")]]/span/text()').extract_first()
                    comment_detail["缺点"] = cmt_detl.xpath('./div[b[contains(text(),"缺点")]]/span/text()').extract_first()
                    comment_detail["外观"] = cmt_detl.xpath('./div[b[contains(text(),"外观")]]/span/text()').extract_first()
                    comment_detail["内饰"] = cmt_detl.xpath('./div[b[contains(text(),"内饰")]]/span/text()').extract_first()
                    comment_detail["空间"] = cmt_detl.xpath('./div[b[contains(text(),"空间")]]/span/text()').extract_first()
                    comment_detail["配置"] = cmt_detl.xpath('./div[b[contains(text(),"配置")]]/span/text()').extract_first()
                    comment_detail["动力"] = cmt_detl.xpath('./div[b[contains(text(),"动力")]]/span/text()').extract_first()
                    comment_detail["操控"] = cmt_detl.xpath('./div[b[contains(text(),"操控")]]/span/text()').extract_first()
                    comment_detail["油耗"] = cmt_detl.xpath('./div[b[contains(text(),"油耗")]]/span/text()').extract_first()
                    comment_detail["舒适"] = cmt_detl.xpath('./div[b[contains(text(),"舒适")]]/span/text()').extract_first()

                # print(username, pushtime, car_type, buy_time, buy_loca, buy_shop, buy_cost, oil_cost, mileage_, zh_Score,
                #       buyimage, cmt_detl)
                item['username'] = username
                item['pushtiem'] = pushtime
                item['car_type'] = car_type
                item['buy_time'] = buy_time
                item['buy_loca'] = buy_loca
                if buy_shop:
                    item['buy_shop'] = buy_shop.strip()
                else:
                    item['buy_shop'] = None
                if buy_cost:
                    item['buy_cost'] = buy_cost + '万元'
                else:
                    item['buy_cost'] = None
                if oil_cost:
                    item['oil_cost'] = oil_cost + 'L/100km'
                else:
                    item['oil_cost'] = None
                item['mileage_'] = mileage_
                item['carimage'] = buyimage
                item['cmt_detl'] = comment_detail
                item['update_datetime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                item['collection'] = title
                yield item
        except Exception as e:
            self.error('【parse_detail出错】{},{}'.format(response.url, e))
