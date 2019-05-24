# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals, Request
import time
from autohomebot.file import file


class AutohomebotSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('【Spider opened】: %s' % spider.name)


from fake_useragent import UserAgent
import requests


class AutohomebotDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    def __init__(self, crawler):

        print('[' + time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time())) + ']', "【init】")

        self.proxy = None  # 默认代理
        self.ua = UserAgent()
        # 若settings中没有设置RANDOM_UA_TYPE的值默认值为random，
        # 从settings中获取RANDOM_UA_TYPE变量，值可以是 random ie chrome firefox safari opera msie
        self.ua_type = crawler.settings.get('RANDOM_UA_TYPE', 'random')
        self.proxy_pool_url = crawler.settings.get('PROXY_POOL_URL')

    def infoPrint(self, message):
        print('[' + time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time())) + '][INFO]' + message)

    def get_ua(self):
        print('[' + time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time())) + ']', "get_ua")
        '''根据settings的RANDOM_UA_TYPE变量设置每次请求的User-Agent'''
        return getattr(self.ua, self.ua_type)

    def get_proxy(self):
        '''获取代理'''

        try:
            response = requests.get(self.proxy_pool_url)
            if response.status_code == 200:
                return "http://{}".format(response.text)
        except ConnectionError:
            print('[' + time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(time.time())) + ']', '【获取代理失败!】')
            return None

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls(crawler)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    '''
    当每个request通过下载中间件时，该方法被调用。
    '''
    # 处理请求
    def process_request(self, request, spider):
        # ua=self.get_ua()
        # request.headers['User-Agent']=ua #.setdefault('User-Agent', ua)
        self.infoPrint('【是否重试】:' + ('是' if request.meta.get('retry') else '否'))
        # spider.info('【是否重试】:' + ('是' if request.meta.get('retry') else '否'))

        # old_proxy = request.meta.get('proxy')
        # if self.proxy is None or old_proxy is None or self.proxy == request.meta.get('proxy'):  # 请求被重来,换代理
        #
        #     self.infoPrint('【更换代理】')
        #     # spider.info('【更换代理】')
        #
        #     proxy = self.get_proxy()
        #     if proxy:
        #         self.proxy = proxy
        #
        # request.meta['proxy'] = self.proxy  # "http://wyiyxpjw-2:shxrrlwfql0n@95.216.1.195:80"
        spider.info('【request】' + self.proxy + ' URL:' + request.url)

    # 处理响应
    def process_response(self, request, response, spider):

        # 如果返回不正确则重新请求
        if response.status != 200:
            if response.status == 302:
                self.infoPrint('【被拦截】:' + self.proxy)
                spider.logger.warning('【被拦截】:' + self.proxy)
            elif response.status == 404:
                self.infoPrint('【无法找到文件】:' + self.proxy + ' URL:' + request.url)
                spider.logger.warning('【无法找到文件】:' + self.proxy + ' URL:' + request.url)
            else:
                self.infoPrint('【未知】' + self.proxy + ' ' + str(response.status) + ' URL:' + request.url)
                spider.logger.warning('【未知】' + self.proxy + ' ' + str(response.status) + ' URL:' + request.url)

            return self.get_retry_request(request)
        elif '用户访问安全认证' in response.text:
            self.infoPrint('【出现安全认证】' + response.url)
            spider.logger.warning('【出现安全认证】' + response.url)
            return self.get_retry_request(request)

        if request.meta.get('retryCount') is not None:
            self.infoPrint('【重试次数】' + str(request.meta.get('retryCount')) + ' URL:' + request.url)
            spider.logger.info('【重试次数】' + str(request.meta.get('retryCount')) + ' URL:' + request.url)

        if request.url.startswith(response.url) == False:
            self.infoPrint('【被重定向】' + response.url)
            spider.logger.warning('【被重定向】' + response.url)
            return self.get_retry_request(request)

        # print('【响应200】',response.text)
        return response

    # 请求异常
    def process_exception(self, request, exception, spider):
        '''
        当下载处理器(download handler)或 process_request() (下载中间件)
        抛出异常(包括 IgnoreRequest 异常)时， Scrapy调用 process_exception()
        '''
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain

        # 重试5次则终止该链接尝试
        # if request.meta.get('retryCount') is not None:
        #     if request.meta.get('retryCount') > 5:
        #         spider.info('【超过5次 request】:' + str(request.meta.get('retryCount')) + "次 " + request.url + "  " + request.meta.get('proxy'))
        #         return None

        try:
            oserror = str(exception.osError)
            if oserror == "10060" or oserror == "10061":
                self.infoPrint('【exception】' + request.url + ' ' + str(exception.args))
                spider.logger.error('【exception】' + request.url + ' ' + str(exception.args))
            else:
                self.infoPrint('【exception】' + request.url + ' ' + str(exception.osError))
                spider.logger.error('【exception】' + request.url + ' ' + str(exception.osError))
        except:

            try:
                self.infoPrint('【exception】' + request.url + ' ' + str(exception))
                spider.logger.error('【exception】' + request.url + ' ' + str(exception))
            except:
                pass

            pass

        self.infoPrint('【请求错误】重试')
        spider.logger.info('【请求错误】重试')

        # 重试
        return self.get_retry_request(request)

    def spider_opened(self, spider):
        spider.logger.info('【spider_opened】: %s' % spider.name)

    def get_retry_request(self, request):
        '''获取要重试的请求'''
        try:
            self.proxy = None  # 重置代理
            retry_request = request.copy()
            retry_request.dont_filter = True  # 禁止去重
            retry_request.meta['retry'] = time.time()

            # 重试次数统计
            if request.meta.get('retryCount') is None:
                retry_request.meta['retryCount'] = 1
            else:
                retry_request.meta['retryCount'] = request.meta.get('retryCount') + 1

            return retry_request
        except Exception as e:
            self.infoPrint('【get_retry_request】【获取要重试的请求出错】' + str(e))
            return None
