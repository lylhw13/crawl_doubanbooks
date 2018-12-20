# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy import signals

class UseragentlistSpider(scrapy.Spider):
    name = 'userAgentList'
    #allowed_domains = ['https://developers.whatismybrowser.com']
    start_urls = ['https://developers.whatismybrowser.com/useragents/explore/software_name/chrome/1']

    def __init__(self):
        self.us_file = open('user_agent.txt', 'w')

    def parse(self, response):
        items = response.xpath("//table/tbody/tr")
        for item in items:
            user_agent = item.xpath("./td/a/text()").extract()[0].strip()
            version = item.xpath("./td[2]/text()").extract()[0].strip()
            print(user_agent)
            try:
                if float(version) >= 60:
                    self.us_file.write(user_agent + '\n')
            except Exception:
                pass

        for i in range(2, 10):
            url = 'https://developers.whatismybrowser.com/useragents/explore/software_name/chrome/{0}'.format(i)
            print(url)
            yield Request(url=url, callback=self.parse)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(UseragentlistSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def spider_closed(self):
        print("spider closed")
        self.us_file.close()

