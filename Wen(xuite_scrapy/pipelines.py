# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

class MongoDBPipeline:

    def open_spider(self, spider):

        db_uri = spider.settings.get('MONGODB_URI', 'mongodb://34.84.16.165:27017')

        db_name = spider.settings.get('MONGODB_DB_NAME', 'DB105_test')

        self.db_client = pymongo.MongoClient('mongodb://34.84.16.165:27017')

        self.db = self.db_client[db_name]

    def process_item(self, item, spider):

        self.insert_article(item)

        return item

    def insert_article(self, item):

        item = dict(item)

        self.db.wen_xuite.insert_one(item)#collection名稱

    def close_spider(self, spider):

        self.db_clients.close()


class SpiderXuitePipeline(object):

    def process_item(self, item, spider):

        return item
