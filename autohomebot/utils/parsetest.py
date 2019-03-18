import urllib.parse

import requests

from lxml import etree
import re

# response = requests.get("http://motor.newmotor.com.cn/ZT310R7149/haoping.shtml")
# html = etree.HTML(response.text)
# title_path = html.xpath('//h1')[0]
# print(title_path)
# title_list = title_path.xpath("string(.)")
# # title = ''.join(title_list)
# print(type(title_list))
# print(title_list)
# str = "space-uid-8194.html"
# uid = re.search("\d+",str).group()
# print(type(uid))


# start_time = '2019-03-01'
# base_url = 'http://bbs.tianya.cn'
# resturl = 'http://search.tianya.cn/bbs?q=%E6%B1%BD%E8%BD%A6&pn=1&s=6'
headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
        }
# # last_url = response.xpath('//div[@class="searchListOne"]/ul/li[10]//h3/a/@href').extract_first()
# last_url = "http://bbs.tianya.cn/post-worldlook-1888810-1.shtml"
# last_response = requests.get(url=last_url, headers=headers)
# html = etree.HTML(last_response.text)
# if html.xpath('//div[@class="mb15 cf"]/div[@class="atl-pages"]/form'):
#     last_page_url = html.xpath('//div[@class="mb15 cf"]/div[@class="atl-pages"]/form/a[last()-1]/@href')[0]
#     last_page_url = base_url + last_page_url
#     last_page_response = requests.get(url=last_page_url, headers=headers)
#     html = etree.HTML(last_page_response.text)
# newest_time = html.xpath('//div[@class="atl-item"][last()]//div[@class="atl-info"]/span[2]/text()')[0]
# newest_time = newest_time.replace('时间：', '')
# if newest_time >= start_time:
#     next_num = str(int(re.search(r'pn=(\d+)', resturl).group(1)) + 1)
#     next_url = re.sub(r'pn=\d+', 'pn={}'.format(next_num), resturl)
#     print(next_url)

str1 = '汽车'
kw = urllib.parse.quote(str1)
print(kw)
url = 'http://search.people.com.cn/cnpeople/search.do?pageNum=1&keyword={}&siteName=news&facetFlag=null&nodeType=belongsId&nodeId=0'.format(kw)
response = requests.get(url,headers=headers)
print(response)
if response.status_code == 200:
    with open('1.html','wb') as f:
        f.write(response.text.encode('utf-8'))
