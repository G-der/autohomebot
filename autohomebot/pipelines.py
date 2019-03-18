# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
import logging


class AutohomebotPipeline(object):
    def __init__(self, db_url, db_name):
        self.db_url = db_url
        self.db_name = db_name
        self.logger = logging.getLogger(__name__)

    def process_item(self, item, spider):
        try:
            self.db[item['collection']].insert(dict(item))
        except Exception as e:
            self.logger.error('插入数据库出错,{},{}'.format(item['collection'], e))
        return item

    def open_spider(self, spider):
        self.client = MongoClient(host=self.db_url)
        self.db = self.client[self.db_name]

    def close_spider(self, spider):
        self.client.close()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('MONGODB_URL'), crawler.settings.get('MONGODB_NAME'))
