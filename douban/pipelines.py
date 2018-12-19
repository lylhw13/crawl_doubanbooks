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
        url = item['img_url']
        yield Request(url=url, meta={'img_name': item['img_name']}, dont_filter=True)

    def file_path(self, request, response=None, info=None):
        return os.path.join(os.path.abspath(os.path.dirname(__file__)), "img/{}.jpg".format(request.meta['img_name']))


class DoubanItemPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', db='douban', charset='utf8')
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):

        # insert_seen_url = "insert into seen_url (url) VALUES (%s)"
        # self.cursor.execute(insert_seen_url, [item['url']])
        # self.conn.commit()

        # insert_info = """
        # insert into page_content (title, url, num, info, main_info, publish_date, image_name, image_url, rating_num, rating_people, stars_per, tags)
        # VALUES (%s, %s, %s, %s, %s,%s%s, %s, %s, %s, %s, %s)"""

        insert_info = """
                insert into page_content_new
                (url, id, title, author, publisher, date, info, img_name, img_url, rating, people, stars_per, tags) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        self.cursor.execute(insert_info, (item['url'], item['id'], item['title'],
                                          item['author'], item['publisher'], item['date'], item['info'],
                                          item['img_name'], item['img_url'], item['rating'],
                                          item['people'], item['stars_per'], item['tags']))
        self.conn.commit()

        return item
