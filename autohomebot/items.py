# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BaseItem(scrapy.Item):
    title = scrapy.Field()  # 标题
    username = scrapy.Field()  # 用户名
    usergender = scrapy.Field()  # 用户性别
    userlocation = scrapy.Field()  # 用户所在地
    userage = scrapy.Field()  # 用户年龄
    push_time = scrapy.Field()  # 发表时间
    comment_detail = scrapy.Field()  # 评论详情
    comment_url = scrapy.Field()  # 评论网址
    catch_time = scrapy.Field()  # 抓取时间
    car_type = scrapy.Field()  # 车型
    bbs_name = scrapy.Field()  # 论坛名
    sonbbs_name = scrapy.Field()  # 子论坛名
    collection = scrapy.Field()  # 表名


class AutohomebotItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    """口碑之家"""
    collection = scrapy.Field()  # 表名
    publish_date = scrapy.Field()
    publish_addr = scrapy.Field()
    buy_date = scrapy.Field()
    brand = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    page_url = scrapy.Field()
    subnav_title = scrapy.Field()
    url = scrapy.Field()
    comment_date = scrapy.Field()
    comment_content = scrapy.Field()
    member_id = scrapy.Field()
    comment_addr = scrapy.Field()
    # comment_list=scrapy.Field()
    update_datetime = scrapy.Field()  # 插入记录的时间


class PcautoItem(scrapy.Item):
    """太平洋汽车网"""
    collection = scrapy.Field()  # 表名
    username = scrapy.Field()
    pushtiem = scrapy.Field()
    car_type = scrapy.Field()
    buy_time = scrapy.Field()
    buy_loca = scrapy.Field()
    buy_shop = scrapy.Field()
    buy_cost = scrapy.Field()
    oil_cost = scrapy.Field()
    mileage_ = scrapy.Field()
    zh_Score = scrapy.Field()
    carimage = scrapy.Field()
    cmt_detl = scrapy.Field()
    update_datetime = scrapy.Field()  # 插入记录的时间


class ZhihuItem(scrapy.Item):
    """知乎"""
    collection = scrapy.Field()  # 表名
    question = scrapy.Field()
    username = scrapy.Field()
    userfans = scrapy.Field()
    user_url = scrapy.Field()
    ans__url = scrapy.Field()
    ans_detl = scrapy.Field()
    pushtime = scrapy.Field()
    follower = scrapy.Field()
    anscommt = scrapy.Field()
    update_datetime = scrapy.Field()  # 插入记录的时间


class NiumoKBItem(scrapy.Item):
    """摩托"""
    title = scrapy.Field()
    collection = scrapy.Field()
    username = scrapy.Field()
    usergender = scrapy.Field()
    userlocation = scrapy.Field()
    push_time = scrapy.Field()
    comment_detail = scrapy.Field()
    comment_url = scrapy.Field()
    # comment_type = scrapy.Field()
    catch_time = scrapy.Field()
    data_from = scrapy.Field()
    car_type = scrapy.Field()


class urlitems(scrapy.Item):
    """url提取"""
    url = scrapy.Field()
    name = scrapy.Field()
    collection = scrapy.Field()


class ArticleItem(scrapy.Item):
    kw = scrapy.Field()  # 搜索关键字
    type = scrapy.Field()
    title = scrapy.Field()
    author = scrapy.Field()
    push_time = scrapy.Field()
    source = scrapy.Field()
    url = scrapy.Field()
    detail = scrapy.Field()
    catch_time = scrapy.Field()
    collection = scrapy.Field()  # 表名

