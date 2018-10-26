# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb

from scrapy.pipelines.images import ImagesPipeline
import os.path
from scrapy.http import Request

class DoubanPipeline(object):
    def process_item(self, item, spider):
        return item

class DownloadImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        url = item['image_url']
        yield Request(url=url, meta={'image_name': item['image_name']}, dont_filter=True)

    def file_path(self, request, response=None, info=None):
        return os.path.join(os.path.abspath(os.path.dirname(__file__)), "images/{}.jpg".format(request.meta['image_name']))


class DoubanItemPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', db='douban', charset='utf8')
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):

        # insert_seen_url = "insert into seen_url (url) VALUES (%s)"
        # self.cursor.execute(insert_seen_url, [item['url']])
        # self.conn.commit()

        insert_info = """
        insert into page_content (title, url, num, info, image_name, image_url, rating_num, rating_people, stars_per, tags)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        self.cursor.execute(insert_info, (item['title'], item['url'], item['num'], item['info'],
                                          item['image_name'], item['image_url'], item['rating_num'],
                                          item['rating_people'], item['stars_per'], item['tags']))
        self.conn.commit()

        return item
