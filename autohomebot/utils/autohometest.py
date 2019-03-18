import requests
from lxml import etree

# url = "https://club.autohome.com.cn/bbs/forum-o-210463-1.html"
url = "https://club.autohome.com.cn/bbs/thread/07a4f590f8959457/68389213-1.html"
headers = {
            'Accept': 'text/html, application/xhtml+xml, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,ja-JP;q=0.5',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Cookie': '__ah_uuid=F4D914F4-FDBC-494C-9605-823FFABBA23E; fvlid=1550793938040KE8lxlphks; sessionip=121.15.166.89; sessionid=A664C535-7DF2-4769-BAE3-D136F691235F%7C%7C2019-02-22+08%3A05%3A39.449%7C%7Cwww.baidu.com; area=440303; ahpau=1; cookieCityId=110100; sessionuid=A664C535-7DF2-4769-BAE3-D136F691235F%7C%7C2019-02-22+08%3A05%3A39.449%7C%7Cwww.baidu.com; historybbsName4=o-200063%7C%E6%91%A9%E6%89%98%E8%BD%A6%2Co-210063%7C%E5%AE%9D%E9%A9%AC%E6%91%A9%E6%89%98%E8%BD%A6%2Co-210163%7C%E5%93%88%E9%9B%B7%E6%91%A9%E6%89%98%E8%BD%A6%2Co-210263%7C%E6%9D%9C%E5%8D%A1%E8%BF%AA%E6%91%A9%E6%89%98%E8%BD%A6%2Co-210763%7C%E6%9C%AC%E7%94%B0%E6%91%A9%E6%89%98%E8%BD%A6%2Co-210863%7C%E6%98%A5%E9%A3%8E%E6%91%A9%E6%89%98%E8%BD%A6; __utmc=1; __utma=1.1095916077.1551428904.1551428904.1551664077.2; __utmz=1.1551664077.2.2.utmcsr=i.autohome.com.cn|utmccn=(referral)|utmcmd=referral|utmcct=/13528955; pcpopclub=61b60ea377f645dab77dd008bc44619905b86483; clubUserShow=95970435|66|6|afq79a|0|0|0||2019-03-04 09:49:02|2; autouserid=95970435; sessionuserid=95970435; ASP.NET_SessionId=0ksjpivubimrhrd5c33irntt; Hm_lvt_c5241958b568d64c9f23212513a22b7f=1551664328; Hm_lpvt_c5241958b568d64c9f23212513a22b7f=1551664342; sessionvid=21195B17-7559-4D21-968E-27C1E62F09D2; ahpvno=16; sessionlogin=6c77e790196044669901e1d79be7929705b86483; ref=www.baidu.com%7C0%7C0%7C0%7C2019-03-04+11%3A00%3A55.511%7C2019-02-22+08%3A05%3A39.449; ahrlid=15516684531643R8zLe5Cau-1551669306268'
        }
response = requests.get(url=url, headers=headers)
html = etree.HTML(response.text)

for each in html.xpath('//div[@id="maxwrap-reply"]/div[@class="clearfix contstxt outer-section"]'):
    try:
        commentpath = each.xpath('.//div[@class="x-reply font14"]')[0]
        comtstr = commentpath.xpath('string(.)').trip()
        print(comtstr)
    except Exception as e:
        print(e)


