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

reply_str = "回复()"
reply_num = re.search(r"\d+", reply_str)
if reply_num:
    print(True)


