# -*- coding: utf-8 -*-

import requests
from scrapy.selector import Selector
import MySQLdb
import time

conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root',db='douban', charset='utf8')
cursor = conn.cursor()

def crawl_ips():
    headers = {"User-Agent": "Mozilla/5.0 (X11; NetBSD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36"}
    for page in range(16, 30):
        time.sleep(30)
        print('crawl page {0}'.format(page))
        re = requests.get("http://www.xicidaili.com/nn/{0}".format(page), headers=headers)
        selector = Selector(text=re.text)

        all_trs = selector.css("#ip_list tr")

        ip_list = []
        for tr in all_trs[1:]:
            speed_str = tr.css(".bar::attr(title)").extract_first()
            if speed_str:
                speed = float(speed_str.split('秒')[0])

            all_texts = tr.css("td::text").extract()

            ip = all_texts[0]
            port = all_texts[1]
            port_type = all_texts[5]

            if port_type.startswith('HTTP') and speed < 1:
                ip_list.append((ip, port, port_type, speed))

        for ip_info in ip_list:
            cursor.execute(
                "insert ignore into xici_proxy(ip, port, port_type,speed) VALUES('{0}', '{1}', '{2}', {3})".format(
                    ip_info[0], ip_info[1], ip_info[2], ip_info[3])
            )
            conn.commit()

class GetIP(object):
    def delete_ip(self, ip):
        delete_sql = """
            delete from xici_proxy where ip ='{0}'""".format(ip)
        cursor.execute(delete_sql)
        cursor.commit()
        return True

    def judge_ip(self,ip, port, port_type):
        http_url = 'https://www.baidu.com/'
        proxy_url = '{0}://{1}:{2}'.format(port_type, ip, port)
        try:
            proxy_dict = {
                port_type:proxy_url
            }
            response = requests.get(http_url, proxies=proxy_dict)
        except Exception as e:
            print('Invalid ip and port')
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code>=200 and code<300:
                print('effective ip')
                return True
            else:
                print('Invalid ip and port')
                self.delete_ip(ip)
                return False

    def get_random_ip(self):
        random_sql = """
        SELECT ip,port,port_type FROM xici_proxy
        ORDER BY RAND()
        LIMIT 1
        """
        result = cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            port_type = ip_info[2]

            if self.judge_ip(ip, port, port_type):
                return '{0}://{1}:{2}'.format(port_type, ip, port)
            else:
                return self.get_random_ip()


if __name__ == "__main__":
    print(crawl_ips())
    #getip = GetIP()
    #print(getip.get_random_ip())