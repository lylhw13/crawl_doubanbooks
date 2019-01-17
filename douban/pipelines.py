# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import MySQLdb

from scrapy.pipelines.images import ImagesPipeline
import os.path
from scrapy.http import Request
from scrapy.exceptions import CloseSpider
import time

class DoubanPipeline(object):
    def process_item(self, item, spider):
        return item

class DownloadImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['status'] != 'ok':
            return
        url = item['img_url']
        if url.split('/')[-1] != 'update_image':
            yield Request(url=url, meta={'img_name': item['img_name']}, dont_filter=True)

    def file_path(self, request, response=None, info=None):
        # return os.path.join(os.path.abspath(os.path.dirname(__file__)), "img/{}.jpg".format(request.meta['img_name']))
        return os.path.join("img/{}.jpg".format(request.meta['img_name']))


import re
urlpat = re.compile(r'.* @ (https://book\.douban\.com/subject/(\d*)/?)')

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

        # if item['status'] == '404':
        #     # insert_404_url = "INSERT IGNORE INTO 404_url (id,url) VALUES ('{0}','{1}')".format(item['id'],item['url'])
        #     # try:
        #     #     self.cursor.execute(insert_404_url)
        #     #     self.conn.commit()
        #     # except Exception as e:
        #     #     print(e)
        #     #     raise CloseSpider('insert into 404_url encounter error')
        #
        #     # set the 404 url state to 4
        #     update_urls = "insert into all_urls (id,url,state) values (%s,%s,%s) on duplicate key update state=values(state)"
        #     try:
        #         self.cursor.execute(update_urls, (item['id'], item['url'], 4))
        #         self.conn.commit()
        #     except Exception as e:
        #         print(e)
        #         raise CloseSpider("update all_urls encounter error")
        #     return

        if item['status'] in ['301', '404']:
            update_urls = "insert into all_urls (id,url,state,description) " \
                          "values (%s,%s,%s,%s) on duplicate key update state=values(state)"

            try:
                self.cursor.execute(update_urls, (item['id'], item['url'], item['status'], item['description']))
                self.conn.commit()
            except Exception as e:
                print(e)
                raise CloseSpider("update all_urls 301 and 404 encounter error")
            return

        if item['status'] == 'wrong':
            insert_wrong_url = '''
            INSERT IGNORE INTO wrong_url (url) VALUES ('{0}')
            '''.format(item['url'])

            self.cursor.execute(insert_wrong_url)
            self.conn.commit()
            return

        # insert into page_content_new
        insert_info = """
                insert into page_content_new
                (url, id, title, author, publisher, date, info, img_name, img_url, rating, people, stars_per, tags, 
                comments, reviews, query_date) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        try:
            self.cursor.execute(insert_info, (item['url'], item['id'], item['title'],
                                              item['author'], item['publisher'], item['date'], item['info'],
                                              item['img_name'], item['img_url'], item['rating'],
                                              item['people'], item['stars_per'], item['tags'],
                                              item['comments'], item['reviews'],
                                              time.strftime('%Y-%m-%d', time.localtime())))
            self.conn.commit()
        except Exception as e:
            print(e)
            # raise CloseSpider("insert page_content_new encounter error")

        # insert into all_urls on duplicate key
        update_urls = "insert into all_urls (id,url,state) values (%s,%s,%s) on duplicate key update state=values(state)"
        try:
            self.cursor.execute(update_urls,(item['id'],item['url'], 1))
            self.conn.commit()
        except Exception as e:
            print(e)
            raise CloseSpider("update all_urls to 1 encounter error")

        # insert ignore into all_urls
        insert_urls = '''insert ignore into all_urls (id,url,state) values '''
        urls_para = []
        for relate_book in item['relate_books']:
            if relate_book:
                mat = urlpat.match(relate_book)
                if mat:
                    url = mat.group(1)
                    num = mat.group(2)
                    urls_para.append("('{0}','{1}','{2}')".format(num,url,0))

        if len(urls_para) != 0:
            insert_urls += ', '.join(urls_para)
            try:
                self.cursor.execute(insert_urls)
                self.conn.commit()
            except Exception as e:
                print(e)
                raise CloseSpider("insert all_urls encounter error")

        # insert into relate_books
        insert_relation = """
                INSERT IGNORE INTO relate_books
                (title, A, B, C, D, E, F, G, H, I, J)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        if len(item['relate_books']) < 10:
            item['relate_books'].extend([''] * (10 - len(item['relate_books'])))
        try:
            self.cursor.execute(insert_relation, ('{0}-{1}'.format(item['title'],item['id']), *item['relate_books']))
            self.conn.commit()
        except Exception as e:
            print(e)
            raise CloseSpider("insert relate_books encounter error")


        return item
