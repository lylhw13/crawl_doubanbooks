# -*- coding=utf-8 -*-

from urllib import request

# 要访问的目标页面
#targetUrl = "http://test.abuyun.com"
targetUrl = "http://proxy.abuyun.com/switch-ip"
# targetUrl = "http://proxy.abuyun.com/current-ip"

# 代理服务器
proxyHost = "http-cla.abuyun.com"
proxyPort = "9030"

# 代理隧道验证信息
# proxyUser = "H9113R68750H57SC"
# proxyPass = "408F84BD29B6E6E6"
#
# proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
#     "host": proxyHost,
#     "port": proxyPort,
#     "user": proxyUser,
#     "pass": proxyPass,
# }
#
# proxy_handler = request.ProxyHandler({
#     "http": proxyMeta,
#     "https": proxyMeta,
# })
#
# # auth = request.HTTPBasicAuthHandler()
# # opener = request.build_opener(proxy_handler, auth, request.HTTPHandler)
#
# opener = request.build_opener(proxy_handler)
#
# opener.addheaders = [("Proxy-Switch-Ip", "yes")]
# request.install_opener(opener)
# resp = request.urlopen(targetUrl).read()
#
# print(resp.decode('utf-8'))
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
        opener.addheaders = [("Proxy-Switch-Ip", "yes")]
        opener.addheaders = [('User-Agent', GetUA().get_random_ua())]
        #opener.addheaders = [('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')]
        #opener.addheaders = [('Connection', 'keep-alive')]
        opener.addheaders = [('Accept-Encoding','gzip, deflate, br')]
        opener.addheaders = [('Accept-Language','zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7,en-US;q=0.6')]
        opener.addheaders = [('Cache-Control','max-age=0')]

        #request.install_opener(opener)
        return opener

    def showProxy(self):
        opener = self.preRequset()

        request.install_opener(opener)
        resp = request.urlopen(targetUrl).read()
        print("-" * 30 + resp.decode('utf-8'))

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
    user = "H40Z0M7J2MGBMX2C"
    passwd = "DFD3C823708AC565"
    localabyun = abyun(user, passwd)
    urls = ["https://httpbin.org/headers", "https://httpbin.org/ip", "https://httpbin.org/user-agent"]
    for url in urls:
        localabyun.showURL(url)
    localabyun.showProxy()


