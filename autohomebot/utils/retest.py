import math
import re

# str1 = '({"status":0,"data":{"list":[{"DocID":1124228668,"Title":"提振经济信心　增强发展后劲——海外人士积极评价中国减税降费举措","NodeId":113352,"PubTime":"2019-03-13 09:35:31","LinkUrl":"http://www.xinhuanet.com/politics/2019-03/13/c_1124228441.htm","Abstract":"今年政府工作报告提出，全年减轻企业税收和社保缴费负担近2万亿元。海外观察人士表示，中国政府此次加大减税降费力度，将提振实体经济发展信心，激发传统产业转型升级积极性，促进经济稳定增长和经济结构调整。","keyword":null,"Editor":null,"Author":"冯文雅","IsLink":1,"SourceName":"新华网","PicLinks":"","IsMoreImg":0,"imgarray":[],"SubTitle":null,"Attr":63,"m4v":null,"tarray":[],"uarray":[],"allPics":[],"IntroTitle":null,"Ext1":null,"Ext2":null,"Ext3":null,"Ext4":null,"Ext5":null,"Ext6":null,"Ext7":null,"Ext8":null,"Ext9":null,"Ext10":null}]},"totalnum":1000} )'
# a = re.search(r'({.*})', str1).group()
# print(a)

# str2 = 'http://forum.home.news.cn/list/50-0-0-1.html'
# str3 = 'http://auto.people.com.cn/GB/1049/index1.html'
# page_num = re.search(r'index(\d+)', str3)
# page_num = str(int(page_num.group(1)) + 1)
# url = re.sub('index\d+', 'index'+page_num, str3)
# print(url)

# str4 = '2019年03月14日07:37  来源：'
# time_str = str4.replace('  来源：','')
# print(time_str)

# url = 'http://tieba.baidu.com/p/6026884976?pid=123955409703&cid=123957219373#123957219373'
# new_url = url.split("?", 1)[0]
# pid = re.search("pid=(\d+)",url.split("?", 1)[1]).group(1)
# print(new_url)
# print(pid)

# dict1 = {'abc':1}
# print(dict1.get("abc"))

# reply_str = "回复()"
# reply_num = re.search(r"\d+", reply_str)
# if reply_num:
#     print(True)

# str1 = '({"watershed":100,"sellerRefundCount":0,"isRefundUser":true,"showPicRadio":true,"data":{"impress":[],"count":{"normal":0,"totalFull":27,"total":27,"bad":0,"tryReport":0,"goodFull":27,"additional":1,"pic":2,"good":27,"hascontent":0,"correspond":0},"attribute":[],"newSearch":false,"correspond":"0.0","spuRatting":[]},"skuFull":false,"isShowDefaultSort":true,"askAroundDisabled":true,"skuSelected":false})'
# str2 = re.search(r'\((.*)\)', str1).group(1)
# print(str2)
# total = 446
# max_page = math.ceil(total / 20)
# print(max_page)

# str1 =  'http://auto.163.com/19/0225/06/E8RG4RR60008856S.html'
# id=re.search('//.*/(.*?).html',str1).group(1)
# print(id)

# str = " http://auto.163.com/special/auto_newenergy_02/\#subtab "
# new_url = str.replace('\\','/')
# print(new_url)

# str1 = '106.12.214.93:16817|106.12.214.74:16817|106.12.214.92:16817|106.12.23.242:16817|180.76.154.61:16817|180.76.250.144:16817|106.12.23.196:16817|116.255.191.105:16817|106.12.24.95:16817|180.76.181.214:16817'
# list = str1.split('|')
# print(list)
import requests

url = 'http://kps.kdlapi.com/api/getkps/?orderid=945555752864198&num=3&pt=1&sep=1'
r = requests.get(url, timeout=8)
if r.status_code == 200:
    text = r.text
    print(text)
    ip = re.findall(r'\d+.\d+.\d+.\d+:\d+',text)
    print(ip)
