import re
import sys
sys.setrecursionlimit(10000)
import requests
import json
import time
from pymongo import MongoClient
import multiprocessing


class ZhiHuSPider():
    def __init__(self, kw):
        self.kw = kw
        self.db_url = "localhost"  # 数据库url
        self.db_name = "autohome"  # 数据库名
        self.db = MongoClient(self.db_url)[self.db_name]  # 数据库实例对象
        self.start_time = "2017-01-01"

    def get_data(self, url):
        """获取json数据"""
        headers = {"authority": "www.zhihu.com",
                   # 'Host': 'www.zhihu.com',
                   'Content-Type': 'ext/html;charset=utf-8',
                   'Referer': 'https://www.zhihu.com/',
                   "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36"
                   }
        response = requests.get(url=url, headers=headers)
        # print(response.text)
        # print(response.content)
        # print(response.encoding)
        return response

    def parse_time(self, sec):
        """处理时间格式"""
        timeArray = time.localtime(sec)  # 秒数
        otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return otherStyleTime

    def wash(self, str):
        """去除格式"""
        return re.sub(r'<.*?>', '', str)

    def parse_comment(self, type, id, title):
        """解析评论"""  # answers
        comment_count = 0
        while True:
            time.sleep(1.5)
            url = 'https://www.zhihu.com/api/v4/{}/{}/comments?include=data%5B%2A%5D.author%2Ccollapsed%2Creply_to_author%2Cdisliked%2Ccontent%2Cvoting%2Cvote_count%2Cis_parent_author%2Cis_author&limit=10&offset={}&order=reverse&status=open'.format(
                type, id, comment_count)
            response = self.get_data(url)
            response.encoding = 'utf8'  #
            comment_data = json.loads(response.text)
            # print(response.text)
            print("正在解析评论:{}".format(url))
            for obj in comment_data["data"]:
                item = {}
                try:
                    item["title"] = title
                    item["username"] = obj["author"]["member"]["name"]  # 用户名
                    item["usergender"] = None  # 用户性别
                    try:
                        if obj["object"]["author"]["member"]["gender"] == 0:
                            item["usergender"] = "女"
                        elif obj["object"]["author"]["member"]["gender"] == 1:
                            item["usergender"] = "男"
                    except:
                        pass
                    item["userlocation"] = None  # 用户所在地
                    item["push_time"] = self.parse_time(obj["created_time"])  # 发表时间

                    if item["push_time"] < self.start_time:  # 若发表时间不符，废止
                        continue
                    item["comment_detail"] = self.wash(obj["content"])  # 评论详情
                    item["comment_url"] = obj["url"]  # TODO 评论网址无法访问，应返回问题网址
                    item["catch_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 抓取时间
                    item["collection"] = "(知乎)" + "自动驾驶" # 表名
                    item["car_type"] = None  # 车型
                    item["bbs_name"] = "知乎"
                    item["sonbbs_name"] = None
                    item["userage"] = None
                    item["keyword"] = self.kw
                    self.db[item['collection']].insert(dict(item))
                except Exception as e:
                    print("获取评价失败【URL】:{},错误信息:{}".format(obj["url"], e))
            if comment_data["paging"]["is_end"] is False:  # 尝试获取下一页链接
                comment_count += 10
            else:
                break

    def main(self):
        result_count = 0
        page_count = 1
        while True:
            url = "https://www.zhihu.com/api/v4/search_v3?t=general&q={}&correction=1&offset={}&limit=10&lc_idx=13&show_all_topics=0&search_hash_id=18f445502a39ec0c1e5a85a60b366812&vertical_info=0%2C1%2C1%2C0%2C0%2C0%2C0%2C0%2C0%2C1".format(
                self.kw, result_count)
            response = self.get_data(url)
            response.encoding = 'utf8'
            time.sleep(3)
            print("正在解析第【{}】页数据...".format(page_count))
            print(url)
            page_count += 1
            # print(response.text)
            search_data = json.loads(response.text)
            for obj in search_data["data"]:
                item = {}
                try:
                    type = obj["object"]["type"]
                    item["title"] = self.wash(obj["highlight"]["title"])  # 标题
                    item["username"] = obj["object"]["author"]["name"]  # 用户名
                    item["usergender"] = None  # 用户性别
                    try:
                        if obj["object"]["author"]["gender"] is 0:
                            item["usergender"] = "女"
                        elif obj["object"]["author"]["gender"] is 1:
                            item["usergender"] = "男"
                    except:
                        pass
                    item["userlocation"] = None  # 用户所在地
                    item["push_time"] = self.parse_time(obj["object"]["created_time"])  # 发表时间
                    if item["push_time"] < self.start_time:
                        continue
                    item["comment_detail"] = self.wash(obj["object"]["content"])  # 评论详情
                    item["comment_url"] = obj["object"]["url"]  # 评论网址

                    item["catch_time"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())  # 抓取时间
                    item["collection"] = "(知乎)" + "自动驾驶"  # 表名
                    item["car_type"] = None  # 车型
                    # item["data_from"] = '知乎'
                    item["bbs_name"] = "知乎"
                    item["sonbbs_name"] = None
                    item["userage"] = None
                    item["keyword"] = self.kw
                    # 插入数据
                    self.db[item['collection']].insert(dict(item))

                    # 尝试获取评论
                    try:
                        if obj["object"]["comment_count"] is not 0:
                            type = type + "s"
                            id = obj["object"]["id"]
                            self.parse_comment(type, id, item["title"])
                    except:
                        pass
                except Exception as e:
                    print("解析失败,错误信息:", e.__traceback__.tb_lineno, e)
            if search_data["paging"]["is_end"] is False:  # 尝试获取下一页链接
                result_count += 10
            else:
                break


if __name__ == '__main__':
    KW_LIST = ["自动驾驶", "无人驾驶", "智能网联汽车",
               "自动驾驶 L3级别", "自动驾驶 L4级别",
               "无人出租车", "无人车", "自动驾驶 视觉融合",
               "自动驾驶 V2X", "自动驾驶 激光雷达", "自动驾驶 深度学习",
               "自动驾驶 高精度地图", "自动驾驶 路径规划", "自动驾驶 AI",
               "自动驾驶 算法", "自动驾驶牌照", "自动驾驶示范区",
               "自动驾驶 示范运营", "自动泊车", "自动驾驶 智慧交通",
               "无人驾驶小镇", "自动驾驶 5G示范区", "自动驾驶 智能化"
               ]
    pool = multiprocessing.Pool(3)
    for kw in KW_LIST:
        spider = ZhiHuSPider(kw)
        pool.apply_async(spider.main())
    pool.close()
    pool.join()
