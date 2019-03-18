import requests
import scrapy
from lxml import etree
from autohomebot.settings import DEFAULT_REQUEST_HEADERS


class urlSpider(object):
    def get_page(self, url):
        response = requests.get(url, headers=DEFAULT_REQUEST_HEADERS)
        html = etree.HTML(response.text)
        return html

    def get_url(self):
        start_url = []
        keyword_list = ['悦酷GZ150', '力帆KP150 ','巧格i','劲丽110Fi','优友125','尚领125']   # ['佳御', '幻影', '幻鲨', '喜鲨']
        for keyword in keyword_list:
            index = 0
            base_url = 'http://zhannei.baidu.com/cse/search?q={}&p={}&s=6678382140702685507&nsid=9&'
            search_url = base_url.format(keyword, index)
            html = self.get_page(search_url)
            # 解析当前页
            for each in html.xpath('//div[@class="result f s0"]/h3'):
                try:
                    url = each.xpath('./a[em]/@href')[0]
                    start_url.append(url)
                except:
                    pass

            # 若存在下一页
            while html.xpath('//a[@class="pager-next-foot n"]'):
                index += 1
                # 下一页url
                next_url = base_url.format(keyword, index)
                # 获取下一页页面
                html = self.get_page(next_url)
                # 解析下一页页面
                for each in html.xpath('//div[@class="result f s0"]/h3'):
                    try:
                        url = each.xpath('./a[em]/@href')[0]
                        start_url.append(url)
                    except:
                        pass
        return start_url


if __name__ == '__main__':
    s = urlSpider()
    s.get_url()
