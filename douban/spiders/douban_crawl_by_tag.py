# -*- coding: utf-8 -*-
import scrapy
import urllib.parse
from scrapy.http import Request
from douban.items import DoubanItem
from scrapy.selector import Selector
from scrapy import signals
import time
import collections
import random
import string


class DoubanCrawlByTagSpider(scrapy.Spider):
    name = 'douban_crawl_by_tag'
    allowed_domains = ['book.douban.com']
    start_urls = ['http://book.douban.com/tag']
    tags = []
    # url = "https://book.douban.com/tag/%E7%BB%8F%E6%B5%8E%E5%AD%A6"
    # Request(url=url, callback=self.parse)

    def __init__(self):
        self.fo_error = open('error_url_list.txt','w+')
        #self.info_tags_dict = {}
        # with open('info_tags.txt','r') as f:
        #     for line in f:
        #         key, value = line.split(':')
        #         if key:
        #             self.info_tags_dict[key] = int(value.strip())

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(DoubanCrawlByTagSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self):
        print("spider closed")
        self.fo_error.close()
        # with open('info_tags.txt','w') as f:
        #     for key, value in self.info_tags_dict.items():
        #         f.write("{0}:{1}\n".format(key, value))

    def start_requests(self):
        base_url = "https://book.douban.com/tag/"
        yield Request(url=self.start_urls[0], callback=self.parse_tags)
        # for tag in self.tags:
        #     url = base_url + urllib.parse.quote(tag)
        #     yield Request(url=url, callback=self.parse)

    def parse_tags(self, response):
        tags = response.xpath("//table[@class='tagCol']/tbody/tr/td/a/@href")
        for tag in tags:
            self.tags.append(tag.extract())
            print(tag.extract())
        base_url = self.start_urls[0]
        for tag in self.tags[:2]:
            print("current tag is {0}".format(tag))
            #url = base_url + urllib.parse.quote(tag)
            url = urllib.parse.urljoin(base_url, urllib.parse.quote(tag))
            yield Request(url=url, callback=self.parse)



    def parse(self, response):
        print(response.url)
        # with open('test.html','wb') as f:
        #     f.write(response.body)
        items = response.xpath("//a[@class='nbg']/@href")
        for item in items:
            url = item.extract()
            if url:
                print(url)
                # yield Request(url=url,
                #         cookies={"Cookie": "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11))},
                #         callback=self.parse_content)
                yield Request(url=url, callback=self.parse_content)
        next_url = response.xpath("//link[@rel='next']/@href").extract()
        if next_url:
            # yield Request(url=urllib.parse.urljoin(response.url,next_url[0]),
            #             cookies={"Cookie": "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11))},
            #             callback=self.parse)
            yield Request(url=urllib.parse.urljoin(response.url,next_url[0]), callback=self.parse)

    def parse_content(self, response):

        item = DoubanItem()

        item['url'] = response.url

        item['id'] = list(filter(None, item['url'].split('/')))[-1]

        try:
            item['title'] = response.xpath("//span[@property='v:itemreviewed']/text()").extract()[0].strip()
            item['img_url'] = response.xpath("//a[@class='nbg']/@href").extract()[0].strip()
            info = response.xpath("//div[@id='info']").extract()[0]

            # 处理评价人数过少的情况
            item['rating'] = response.xpath("//strong[@class='ll rating_num ']/text()").extract()[0].strip()
            if item['rating']:
                item['people'] = response.xpath("//a[@class='rating_people']/span/text()").extract()[0].strip()
            else:
                item['rating'] = '0'
                item['people'] = '0'

        except Exception:
            message = '{0:30} has error during parse_content\n'.format(item['url'])
            print(message)
            self.fo_error.write(message)
            return

        # parse the information
        info_list = [ele.strip() for ele in info.split('<br>')][:-1]    # the last one is </div>, remove it
        info_dict = collections.OrderedDict()
        for ele in info_list:
            ele_else = Selector(text=ele).xpath("//text()").extract()
            ele_list = list(filter(None, [val.strip() for val in ele_else]))

            key = ele_list[0]
            if key[-1] in [':', '：']:
                key = key[:-1]

            # if key in self.info_tags_dict.keys():
            #     self.info_tags_dict[key] +=1
            # else:
            #     self.info_tags_dict[key] = 1

            value = '/'.join([' '.join(val.split()) for val in ele_list[1:] if val not in [':', '：', '/']])
            info_dict[key] = value

        item['info'] = ''
        main_info = {'作者': 'author', '出版社': 'publisher', '出版年': 'date'}
        for key, value in info_dict.items():
            if key in main_info.keys():
                item[main_info[key]] = value
            else:
                item['info'] += "{}:{}\n".format(key, value)
            # if key == '出版年':
            #     item['publish_date'] = value
            # elif key in main_info:
            #     item['main_info'] += "{}:{}\n".format(key, value)

        item['img_name'] = "{0}-{1}".format(item['title'], item['id'])
        tags = response.xpath("//div[@id='db-tags-section']/div/span/a/text()").extract()   #list
        item['tags'] = ','.join(tags)

        stars_per = response.xpath("//span[@class='rating_per']/text()").extract()  #list
        item['stars_per'] = ','.join(stars_per)

        yield item
