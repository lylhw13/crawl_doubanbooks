# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.dupefilter import RFPDupeFilter
from scrapy.downloadermiddlewares.redirect import RedirectMiddleware
from scrapy.utils.request import request_fingerprint
import MySQLdb
import redis
import pandas as pd
import os
import logging
from tools.crawler_xici_ip import GetIP
from tools.crawler_user_agent import GetUA

class DoubanSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class DoubanDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


from fake_useragent import UserAgent


class RandomUserAgentMiddleware(object):
    def __init__(self, crawler):
        super(RandomUserAgentMiddleware,self).__init__()
        # self.ua = UserAgent()
        # self.ua_type = crawler.settings.get("RANDOM_UA_TYPE","random")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):

        # def get_ua():
        #     return getattr(self.ua, self.ua_type)
        #request.headers.setdefault('User-Agent', get_ua())
        request.headers.setdefault('User-Agent', GetUA().get_random_ua())

import base64
import time
from tools.showProxy import abyun
class RandomProxyMiddleware(object):
    def __init__(self):
        self.proxyServer = "http://http-cla.abuyun.com:9030"
        self.proxyUser = "HJNX23202XF23K6C"
        self.proxyPass = "38704CF1EEAD9F0A"
        self.proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((self.proxyUser + ":" + self.proxyPass), "ascii")).decode("utf8")
        self.currentTime = time.time()

    def process_request(self, request, spider):

        # request.meta["proxy"] = GetIP().get_random_ip()
        # print(request.meta['proxy'])

        if time.time() - self.currentTime > 3:
            request.headers['Proxy-Switch-Ip'] = 'yes'
            #abyun(self.proxyUser, self.proxyPass).showProxy()
            self.currentTime = time.time()
            print("change the proxy")


        request.meta["proxy"] = self.proxyServer
        request.headers["Proxy-Authorization"] = self.proxyAuth
        request.headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        request.headers['Accept-Encoding'] = "gzip, deflate, br"
        request.headers['Accept-Language'] = 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6'





class CustomFilterMiddleware(RFPDupeFilter):
    def __init__(self, path=None, debug=False):
        # customer
        conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', db='douban', charset='utf8')
        self.redis_db = redis.Redis(host='127.0.0.1', port=6379, db=4)
        self.redis_data_dict = "seen_url"
        self.redis_db.flushdb()
        if self.redis_db.hlen(self.redis_data_dict) ==0:
            sql = "SELECT url FROM page_content_new"
            df = pd.read_sql(sql, conn)
            for url in df['url'].get_values():
                self.redis_db.hset(self.redis_data_dict, url, 0)

        # original
        self.file = None
        self.fingerprints = set()
        self.logdupes = True
        self.debug = debug
        self.logger = logging.getLogger(__name__)
        if path:
            self.file = open(os.path.join(path, 'requests.seen'), 'a+')
            self.file.seek(0)
            self.fingerprints.update(x.rstrip() for x in self.file)

    def request_seen(self, request):
        # customer
        if self.redis_db.hexists(self.redis_data_dict, request.url):
            return True

        # original
        fp = self.request_fingerprint(request)
        if fp in self.fingerprints:
            return True
        self.fingerprints.add(fp)
        if self.file:
            self.file.write(fp + os.linesep)

# class CustomRedirectMiddleware(RedirectMiddleware):
#
#     def process_response(self, request, response, spider):
#         if (request.meta.get('dont_redirect', False) or
#                 response.status in getattr(spider, 'handle_httpstatus_list', []) or
#                 response.status in request.meta.get('handle_httpstatus_list', []) or
#                 request.meta.get('handle_httpstatus_all', False)):
#             return response
#
#         allowed_status = (301, 302, 303, 307, 308)
#         if 'Location' not in response.headers or response.status not in allowed_status:
#             return response
#
#         location = safe_url_string(response.headers['location'])
#
#         redirected_url = urljoin(request.url, location)
#
#         if response.status in (301, 307, 308) or request.method == 'HEAD':
#             redirected = request.replace(url=redirected_url)
#             return self._redirect(redirected, request, spider, response.status)
#
#         redirected = self._redirect_request_using_get(request, redirected_url)
#         return self._redirect(redirected, request, spider, response.status)