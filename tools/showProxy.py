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

class abyun(object):
    def __init__(self, proxyUser, proxyPass):
        self.proxyUser = proxyUser
        self.proxyPass = proxyPass

    def showProxy(self):

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

        request.install_opener(opener)
        resp = request.urlopen(targetUrl).read()
        print("-" * 30 + resp.decode('utf-8'))

if __name__== "__main__" :
    abyun("", "").showProxy()
