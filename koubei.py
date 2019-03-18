# -*- coding: utf-8 -*-
import copy
import json
import re
import time

import scrapy
from scrapy import Request

from autohomebot.items import AutohomebotItem
import random

def add_schema(url):
    if url.startswith('//'):
        return 'https:' + url
    return url

def get_comment_headers(referer):
    comment_header={
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'reply.autohome.com.cn',
        'Pragma': 'no-cache',
        'Referer': referer
    }
    return comment_header


class KoubeiSpider(scrapy.Spider):
    name = 'koubei'
    allowed_domains =['k.autohome.com.cn','reply.autohome.com.cn','i.autohome.com.cn']

    start_urls = ['https://k.autohome.com.cn/4073']

#    start_urls = ['https://k.autohome.com.cn/4554',
#                'https://k.autohome.com.cn/4428',
#                'https://k.autohome.com.cn/3993',
#                'https://k.autohome.com.cn/4073',
#                'https://k.autohome.com.cn/2761',
#                'https://k.autohome.com.cn/4240',
#                'https://k.autohome.com.cn/4394',
#                'https://k.autohome.com.cn/4343',
#                'https://k.autohome.com.cn/4238',
#                'https://k.autohome.com.cn/4320',
#                'https://k.autohome.com.cn/4321',
#                'https://k.autohome.com.cn/4291',
#                'https://k.autohome.com.cn/3529',
#                'https://k.autohome.com.cn/4264',
#                'https://k.autohome.com.cn/3779',
#                'https://k.autohome.com.cn/4355',
#                'https://k.autohome.com.cn/3827',
#                'https://k.autohome.com.cn/3395',
#                'https://k.autohome.com.cn/4444',
#                'https://k.autohome.com.cn/2955',
#                'https://k.autohome.com.cn/4088',
#                'https://k.autohome.com.cn/4380',
#                'https://k.autohome.com.cn/4218',
#                'https://k.autohome.com.cn/2779',
#                'https://k.autohome.com.cn/3648',
#                'https://k.autohome.com.cn/4262',
#                'https://k.autohome.com.cn/4341',
#                'https://k.autohome.com.cn/3706/stopselling',
#                'https://k.autohome.com.cn/4427',
#                'https://k.autohome.com.cn/2357',
#                'https://k.autohome.com.cn/2664',
#                'https://k.autohome.com.cn/4342',
#                'https://k.autohome.com.cn/4652',
#                'https://k.autohome.com.cn/4624',
#                'https://k.autohome.com.cn/2805',
#                'https://k.autohome.com.cn/2388',
#                'https://k.autohome.com.cn/3575',
#                'https://k.autohome.com.cn/4318',
#                'https://k.autohome.com.cn/4375',
#                'https://k.autohome.com.cn/4597',
#                'https://k.autohome.com.cn/3533',
#                'https://k.autohome.com.cn/4104',
#                'https://k.autohome.com.cn/4015',
#                'https://k.autohome.com.cn/3810/stopselling',
#                'https://k.autohome.com.cn/3884',
#                'https://k.autohome.com.cn/3537/stopselling']

    def info(self, message, isPrint = True):
        #控制台显示消息
        if isPrint == True:
            print('[' + time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time())) +'][INFO]' + message)

        #Log文件输出
        self.logger.info(message)

    def warning(self, message, logOutput = True):
        #控制台显示消息
        print('[' + time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time())) +'][WARNING]' + message)

        #Log文件输出
        if logOutput == True:
            self.logger.warning(message)

    def error(self, message, logOutput = True):
        #控制台显示消息
        print('[' + time.strftime('%Y/%m/%d %H:%M:%S',time.localtime(time.time())) +'][ERROR]' + message)

        #Log文件输出
        if logOutput == True:
            self.logger.error(message)

    #默认处理响应数据
    def parse(self, response): #index page
        self.info("--------------------[一级URL处理]--------------------")
        self.info('汽车之家口碑:[{}]、.状态:[{}]'.format(response.url,response.status))

        #判断是否有详细内容链接
        if response.xpath("//a[@class='btn btn-small fn-left']/@href"):
            #查看全部内容
            detail_urls = response.xpath("//a[@class='btn btn-small fn-left']/@href").extract()
            for url in detail_urls:
                url = add_schema(url)
                yield Request(url, meta={'page_url': response.url, 'subnav_title': response.xpath("//div[@class='subnav-title-name']/a/text()").extract_first()},callback=self.parse_detail,priority=50)

            #判断是否有多页
            if response.xpath("//a[@class='page-item-next']//@href"):#下一页
                next_page = response.xpath("//a[@class='page-item-next']//@href").extract_first()
                self.info('【加载下一页索引页...】')
                yield response.follow(next_page,callback=self.parse)        
        else:
            #页面获取失败重试
            self.warning('加载列表页失败.{}'.format(response.url))

            if '暂无符合该列表的口碑' not in response.text:
                yield Request(response.url, callback=self.parse, dont_filter=True, meta={'retry':time.time()})
                self.warning('加载列表页失败.重试.{}'.format(response.url))

    #【明细数据】处理响应数据
    def parse_detail(self, response):
        self.info('【明细数据】URL{}、状态码:{}'.format(response.url, response.status))

        if response.xpath("//div[contains(@class,'koubei-final')]//div[contains(@class,'title-name')]/b"):#发表时间
            try:
                #获取字段值
                publish_date = response.xpath("//div[contains(@class,'koubei-final')]//div[contains(@class,'title-name')]/b/text()").extract_first()[1:]
                publish_addr = response.xpath("//dl[@class='choose-dl' and dt[contains(text(),'购买地点')]]/dd/text()").extract_first().strip()
                buy_date = response.xpath("//dl[@class='choose-dl' and dt[contains(text(),'购买时间')]]/dd/text()").extract_first().strip()
                brand = response.xpath("//dl[@class='choose-dl' and dt[contains(text(),'购买车型')]]/dd/a/text()").extract_first().strip()
                brand = brand + ' ' + response.xpath("//dl[@class='choose-dl' and dt[contains(text(),'购买车型')]]/dd/a[2]/text()").extract_first()
                title = response.xpath("//title/text()").extract_first()
                page_url = response.meta['page_url']
                subnav_title = response.meta['subnav_title']
                url = response.url
                content = response.xpath("//div[@class='mouth-main']").extract_first()
                content = re.sub(r"(<style(.|\r|\n)+?</style>)|(<script(.|\r|\n)+?</script>)|(<!--(.|\r|\n)+?-->)|(<[^>]*>)|(\r|\n)|(\s+)|(&nbsp;)", "", content)

                #获取项目实例
                items = AutohomebotItem()
                for field in items.fields:
                    try:
                        #动态给字段赋值
                        items[field] = eval(field)
                    except NameError:
                        pass

                #获取评论前提交数据
                itemsTemp = copy.deepcopy(items)
                itemsTemp['comment_date'] = ""
                itemsTemp['comment_content'] = ""
                itemsTemp['member_id'] = ""
                itemsTemp['comment_addr'] = ""
                itemsTemp['update_datetime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                itemsTemp['collection'] = 'autohomekoubei'
                #【插入数据】
                yield itemsTemp

                self.info('【提交主体明细数据】')

                #评论
                koubei_id = response.xpath("//input[@id='hidEvalId']/@value").extract_first()
                comment_url = "https://reply.autohome.com.cn/ShowReply/ReplyJsonredis.ashx?count=10&page=1&id={}&datatype=jsonp&appid=5{}".format(koubei_id,self.get_comment_url_random())
                
                self.info('【首页评论URL】' + comment_url)

                yield Request(comment_url,priority=100,callback=self.parse_comment,headers=get_comment_headers(response.url),meta={'items':items,'page_index':1,'koubei_id':koubei_id})
            except Exception as e:
                self.error('【parse_detail出错】{},{}'.format(response.url,e))

    #【明细数据内容】处理响应数据
    def parse_comment(self, response):
        self.info('【评论明细】{}、状态码:{}'.format(response.url,response.status))

        if response.status == 200 and 'jQuery' in response.text:
            tmp=re.search(r"\{[\s\S]*\}", response.text)
            if tmp:
                jsonObj = json.loads(tmp.group())
                try:
                    items = response.meta['items']

                    if jsonObj['commentlist'] is not None and len(jsonObj['commentlist']) != 0:#有评论返回
                        strCommentList = '【评论数】{}'.format(len(jsonObj['commentlist']))

                        try:
                            self.info(strCommentList)

                            page_index=int(response.meta['page_index']) + 1
                            koubei_id=response.meta['koubei_id']

                            for obj in jsonObj['commentlist']:
                                items1=copy.deepcopy(items)
                                member_id=obj['RMemberId']
                                member_home_url="https://i.autohome.com.cn/{}".format(member_id)
                                items1['member_id']=member_id
                                items1['comment_date']=obj['replydate']
                                items1['comment_content']=obj['RContent']

                                self.info('【评论内容】:' + obj['RContent'])

                                #【委托】获取评论者所在地
                                yield Request(member_home_url,priority=101,dont_filter=True,callback=self.parse_member_home_info,meta={'items':items1}) #从评论者主页找到其所在地
                        except Exception as e:
                            self.error('【获取CommentList出错】' + str(e))
                        #获取下一页评论
                        nextItems = copy.deepcopy(items)
                        comment_url="https://reply.autohome.com.cn/ShowReply/ReplyJsonredis.ashx?count=10&page={}&id={}&datatype=jsonp&appid=5{}".format(page_index,koubei_id,self.get_comment_url_random())
                        
                        self.info('【下一页评论URL】' + comment_url)
                        yield Request(comment_url,priority=100,callback=self.parse_comment,headers=get_comment_headers(response.url),meta={'items':nextItems,'page_index':page_index,'koubei_id':koubei_id})
                except Exception as e:
                    self.error('【评论明细为空】URL：{}、状态码:{}'.format(response.url, response.status))

    #【获取评论者所在地】处理响应数据
    def parse_member_home_info(self, response):
        self.info('【评论者归属地】URL：{}、状态码:{}'.format(response.url,response.status))
        if response.status == 200 and response.xpath("//a[@class='state-pos']"):
            member_addr = response.xpath("//a[@class='state-pos']/text()").extract_first()
            items = response.meta['items']#AutohomebotItem
            items['comment_addr'] = member_addr
            items['update_datetime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            items['collection'] = 'autohomekoubei'
            self.info('【提交数据】')
            #【插入数据】
            yield items
        return None
    
    #获取随机数
    def get_comment_url_random(self):
        def get_timestamp_str():
            return str(time.time()*1000)[:13]
        def get_random_digital_str():
            return str(random.random())[2:]
        return "&callback=jQuery1720{}_{}&_={}".format(get_random_digital_str(),get_timestamp_str(),get_timestamp_str())