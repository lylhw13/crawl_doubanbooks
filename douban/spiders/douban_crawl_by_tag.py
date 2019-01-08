# -*- coding: utf-8 -*-
import scrapy
import urllib.parse
from scrapy.http import Request
from douban.items import DoubanItem
from scrapy.selector import Selector
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import CloseSpider
import time
import collections
import random
import string

from multiprocessing import Process, Queue
from scrapy.utils.project import get_project_settings
import scrapy.crawler as crawler
from twisted.internet import reactor
import MySQLdb
import pandas as pd

class DoubanCrawlByTagSpider(scrapy.Spider):
    name = 'douban_crawl_by_tag'
    #allowed_domains = ['book.douban.com']
    start_urls = ['http://book.douban.com/tag/']
    tags = []
    handle_httpstatus_list = [302, 402, 403, 404, 503]  # to handle the blocked

    def __init__(self):
        #self.fo_error = open('error_url_list.txt','w+')
        #self.info_tags_dict = {}
        # with open('info_tags.txt','r') as f:
        #     for line in f:
        #         key, value = line.split(':')
        #         if key:
        #             self.info_tags_dict[key] = int(value.strip())
        pass

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(DoubanCrawlByTagSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self):
        print("spider closed")
        # self.fo_error.close()
        # with open('info_tags.txt','w') as f:
        #     for key, value in self.info_tags_dict.items():
        #         f.write("{0}:{1}\n".format(key, value))

    def start_requests(self):
        base_url = "https://book.douban.com/tag/"
        tags = []

        # ******method one******
        # with open('tags_local.txt', 'r', encoding='utf-8') as f:
        #     tags_content = f.read()
        #     tags = tags_content.split(',')
        # with open('tags_1.txt', 'r', encoding='utf8') as f:
        #     tags_content = f.read()
        #     tags = tags_content.split(',')

        # tag = tags[random.randrange(0, len(tags))]
        # print('current tag is ' + tag)
        # url = urllib.parse.urljoin(base_url, urllib.parse.quote(tag))
        # yield Request(url=url, callback=self.parse)

        # ******method two******
        # span = 10
        #
        # start = random.randrange(0, len(tags)-span)
        # print(start)
        # for tag in tags[start: start+span]:
        #     print(tag)
        #     url = urllib.parse.urljoin(base_url, urllib.parse.quote(tag))
        #     yield Request(url=url, callback=self.parse)
        #     time.sleep(2)
        # url = "https://book.douban.com/subject/1000269/"
        # yield Request(url=url, callback=self.parse_content)

        # ******method three******
        conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', db='douban', charset='utf8')

        sql = "select url from all_urls where state='0' order by rand() limit 1"
        df = pd.read_sql(sql, conn)
        for url in df['url'].get_values():
            print(url)
            yield Request(url=url, callback=self.parse_content)
        #yield Request(url="https://httpbin.org/headers", callback=self.parse_content)


        #yield Request(url=self.start_urls[0], callback=self.parse_tags)
        # for tag in self.tags:
        #     url = base_url + urllib.parse.quote(tag)
        #     yield Request(url=url, callback=self.parse)

    def parse_tags(self, response):
        tags = response.xpath("//table[@class='tagCol']/tbody/tr/td/a/@href")
        for tag in tags:
            self.tags.append(tag.extract())
            print(tag.extract())
        # with open('tags_local.txt', 'w', encoding='utf-8') as f:
        #     tag_only = [tag.extract().split('/')[-1] for tag in tags]
        #     f.write(",".join(tag_only))
        base_url = self.start_urls[0]
        for tag in self.tags:
            print("current tag is {0}".format(tag))
            url = urllib.parse.urljoin(base_url, urllib.parse.quote(tag))
            yield Request(url=url, callback=self.parse)

    def parse(self, response):      # parse page list
        print(response.url)
        # with open('test.html','wb') as f:
        #     f.write(response.body)
        urls = response.xpath("//a[@class='nbg']/@href").extract()
        for url in urls:
            if url:
                print(url)
                # yield Request(url=url,
                #         cookies={"Cookie": "bid=%s" % "".join(random.sample(string.ascii_letters + string.digits, 11))},
                #         callback=self.parse_content)
                #url = "http://webcache.googleusercontent.com/search?q=cache:" + url
                yield Request(url=url, callback=self.parse_content, errback=self.errback)
        next_page = response.xpath("//link[@rel='next']/@href").extract()
        if next_page:
            yield Request(url=urllib.parse.urljoin(response.url,next_page[0]), callback=self.parse, errback=self.errback)


    def parse_content(self, response):
        #
        # print(response.headers)
        # return
        # print(response.body.decode('utf-8'))
        # return

        item = DoubanItem()

        if response.status != 200:
            if response.status != 404:
                print(response.status)
                print("b"*100 + '  be blocked ')
                raise CloseSpider("Be blocked  ".format(response.status))

        item['url'] = response.url

        item['id'] = list(filter(None, item['url'].split('/')))[-1]

        if response.status == 404:
            item['status'] = '404'
            yield item
            return

        #error_flag = False
        item['status'] = 'ok'

        try:
            item['title'] = response.xpath("//span[@property='v:itemreviewed']/text()").extract()[0].strip()
            item['img_url'] = response.xpath("//a[@class='nbg']/@href").extract()[0].strip()
            info = response.xpath("//div[@id='info']").extract()[0]

            # 处理评价人数过少的情况
            rating_item = response.xpath("//strong[@class='ll rating_num ']/text()").extract()
            item['rating'] = rating_item[0].strip() if len(rating_item) != 0 and len(rating_item[0].strip())!=0 else '0'

            people_item = response.xpath("//a[@class='rating_people']/span/text()").extract()
            item['people'] = people_item[0].strip() if len(people_item) != 0 and len(people_item[0].strip())!=0else '0'


        except Exception:
            message = '{0:30} has error during parse_content\n'.format(item['url'])
            print('c'*150 + message)
            # wait_time = random.random() * 5
            # print('wait time is {}'.format(wait_time))
            # time.sleep(wait_time)
            with open("error_url_list.txt",'a') as f:
                f.write(message + '\n')
            with open('wrong_page_{}.txt'.format(item['id']), 'wb') as f:
                f.write(response.body)
            #self.fo_error.write(message)
            #error_flag = True
            item['status'] = 'wrong'
            raise CloseSpider("Has error in parsing content  ".format(response.status))

        else:
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

            main_info = {'作者': 'author', '出版社': 'publisher', '出版年': 'date'}

            item['info'] = ''      # init
            for key in main_info.keys():
                item[main_info[key]] = ''

            for key, value in info_dict.items():
                if key in main_info.keys():
                    item[main_info[key]] = value
                else:
                    item['info'] += "{}:{}\n".format(key, value)


            # if item['date']:        # format the date to fit mysql format
            #     date_part = item['date'].split('-')
            #     if len(date_part) < 3:
            #         date_part.extend((3 - len(date_part)) * ['0'])
            #     item['date'] = '{0}-{1:0>2}-{2:0>2}'.format(*date_part)

            # item['img_name'] = "{0}-{1}".format(item['title'], item['id'])
            item['img_name'] = "{0}".format(item['id'])
            tags = response.xpath("//div[@id='db-tags-section']/div/span/a/text()").extract()   # list
            item['tags'] = ','.join(tags)

            # with open('tags.txt', 'a', encoding='utf8') as f:
            #     f.write("{0},".format(item['tags']))

            stars_per = response.xpath("//span[@class='rating_per']/text()").extract()  # list
            item['stars_per'] = ','.join(stars_per)

        finally:
            try:
                # handel the relate url
                urls = response.xpath("//div[@class='block5 subject_show knnlike']/div/dl/dd/a/@href").extract()
                for url in urls:
                    yield Request(url=url, callback=self.parse_content)
                names = response.xpath("//div[@class='block5 subject_show knnlike']/div/dl/dd/a/text()").extract()

                item['relate_books'] = ['{0} @ {1}'.format(key.strip(), value) for (key, value) in zip(names, urls)]

            except Exception:
                message = '{0:30} can not parse the relate url during parse_content\n'.format(item['url'])
                print(message)
                self.fo_error.write(message)
                item['relate_books'] = []
                #error_flag = True

            yield item

    def errback(self, failure):
        print("@"*60 + "hadle the failure")
        self.logger.error(repr(failure))


if __name__ == "__main__":

    # def run_spider():
    #     def f(q):
    #         try:
    #             runner = crawler.CrawlerRunner()
    #             deferred = runner.crawl(DoubanCrawlByTagSpider)
    #             deferred.addBoth(lambda _: reactor.stop())
    #             reactor.run()
    #             q.put(None)
    #         except Exception as e:
    #             q.put(e)
    #
    #     q = Queue()
    #     p = Process(target=f, args=(q,))
    #     p.start()
    #     result = q.get()
    #     p.join()
    #
    #     if result is not None:
    #         raise result
    #
    #
    # run_spider()

    while True:
        print('begin')
        process = CrawlerProcess(get_project_settings())
        process.crawl(DoubanCrawlByTagSpider)
        #process.start(stop_after_crawl=False)
        process.start()
        #run_spider()
        time.sleep(10)
        print('$'*100 + "\nwe reade to start the spider")
        time.sleep(10)


