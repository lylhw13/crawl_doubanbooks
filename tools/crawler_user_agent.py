# -*- coding: utf-8 -*-

import requests
from scrapy.selector import Selector
import MySQLdb
import time

conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', db='douban', charset='utf8')
cursor = conn.cursor()


def crawl_ua():
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
    for page in range(1,10):
        time.sleep(10)
        print('crawl page {}'.format(page))
        url = 'https://developers.whatismybrowser.com/useragents/explore/software_name/chrome/{}'.format(page)
        req = requests.get(url=url, headers=header)
        selector = Selector(text=req.text)

        items = selector.xpath("//table/tbody/tr")
        for item in items:
            user_agent = item.xpath("./td/a/text()").extract()[0].strip()
            version = item.xpath("./td[2]/text()").extract()[0].strip()
            os = item.xpath("./td[3]/text()").extract()[0].strip()
            hardware_type = item.xpath("./td[4]/text()").extract()[0].strip()
            print(user_agent)
            cursor.execute(
                'insert into user_agent(id, user_agent, version, os, hardware_type) VALUES("{0}","{1}","{2}","{3}",'
                '"{4}")'.format(0, user_agent, version, os, hardware_type)
            )
            conn.commit()

class GetUA(object):
    def get_random_ua(self):
        random_sql = '''
        SELECT user_agent FROM user_agent
        WHERE version>"60" and os="Windows" and hardware_type="Computer"
        ORDER BY RAND()
        LIMIT 1'''

        result = cursor.execute(random_sql)

        for info in cursor.fetchall():
            ua = info[0]
            return ua
            #print(ua)


if __name__ == '__main__':
    crawl_ua()
