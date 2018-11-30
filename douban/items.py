# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanItem(scrapy.Item):
    # define the fields for your item here like:
    num = scrapy.Field()

    title = scrapy.Field()
    info = scrapy.Field()

    publish_date = scrapy.Field()

    url = scrapy.Field()
    image_url = scrapy.Field()
    image_name = scrapy.Field()
    tags = scrapy.Field()

    rating_num = scrapy.Field()
    stars_per = scrapy.Field()

    rating_people = scrapy.Field()     #评价人数
    pass
