# -*- coding=utf-8 -*-

from urllib import request
from urllib import error

targetUrl = "http://proxy.abuyun.com/switch-ip"

proxyHost = "http-pro.abuyun.com"
proxyPort = "9010"

from tools.crawler_user_agent import GetUA

class abyun(object):
    def __init__(self, proxyUser, proxyPass):
        self.proxyUser = proxyUser
        self.proxyPass = proxyPass
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; NetBSD) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.116 Safari/537.36"}

    def preRequset(self):
        proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
            "user": self.proxyUser,
            "pass": self.proxyPass,
        }

        proxy_handler = request.ProxyHandler({
            "http": proxyMeta,
            "https": proxyMeta,
        })
        opener = request.build_opener(proxy_handler)
        #opener.addheaders = [("Proxy-Switch-Ip", "yes")]
        opener.addheaders.append(('User-Agent', GetUA().get_random_ua()))
        #opener.addheaders = [('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')]
        #opener.addheaders = [('Connection', 'keep-alive')]
        opener.addheaders.append(('Accept-Encoding','gzip, deflate, br'))
        opener.addheaders.append(('Accept-Language','zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6'))
        opener.addheaders.append(('Cache-Control','max-age=0'))
        # request.headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8"
        #
        # request.headers['Cache-Control'] = 'max-age=0'
        # #request.headers['Connection'] = 'keep-alive'
        # #request.headers['Host'] = 'book.douban.com'
        # request.headers['DNT'] = '1'
        # request.headers['Upgrade-Insecure-Requests'] = '1'



        #request.install_opener(opener)
        return opener

    def switch_ip(self):
        opener = self.preRequset()

        request.install_opener(opener)
        try:
            resp = request.urlopen(targetUrl)
        except error.HTTPError as err:
            print(err)
        resp = request.urlopen(targetUrl).read()
        print(resp.decode('utf-8'))

    def showResponse(self):
        opener = self.preRequset()
        url = "https://httpbin.org/headers"
        request.install_opener(opener)
        rep = request.urlopen(url).read()
        print(rep.decode('utf-8'))
    def showIp(self):
        opener = self.preRequset()
        url = "https://httpbin.org/ip"
        request.install_opener(opener)
        rep = request.urlopen(url).read()
        print(rep.decode('utf-8'))
    def showAgent(self):
        pass

    def showURL(self,url):
        opener = self.preRequset()
        request.install_opener(opener)
        rep = request.urlopen(url).read()
        print(rep.decode('utf-8'))

if __name__== "__main__" :
    print(GetUA().get_random_ua())
    user = "HQ4M5U3IBDW9912P"
    passwd = "5122EDD88D113B9A"
    localabyun = abyun(user, passwd)
    # urls = ["https://httpbin.org/user-agent", "https://httpbin.org/headers", "https://httpbin.org/ip"]
    # for url in urls:
    #     localabyun.showURL(url)


