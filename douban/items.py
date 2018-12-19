# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanItem(scrapy.Item):
    # define the fields for your item here like:
    url = scrapy.Field()
    id = scrapy.Field()

    title = scrapy.Field()
    author = scrapy.Field()
    publisher = scrapy.Field()
    date = scrapy.Field()

    info = scrapy.Field()

    img_name = scrapy.Field()
    img_url = scrapy.Field()
    rating = scrapy.Field()
    people = scrapy.Field()     #评价人数
    stars_per = scrapy.Field()

    tags = scrapy.Field()
