# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo

class DangdangspiderPipeline(object):
    def __init__(self):
        self.count = 1
        self.db= self.conn_mongo()

    def conn_mongo(self):
        client = pymongo.MongoClient(host="localhost",port=27017)
        print(client)
        return client.dangdang

    def process_item(self, item, spider):
        # print(self.count,item)
        self.db.dangdang.insert(dict(item))
        self.count+=1
        return item

