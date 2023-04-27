# -*- coding: UTF-8 -*-
"""翻译"""

import asyncio
import time
import random
import re
import hashlib
from urllib.parse import unquote,quote
from fake_useragent import UserAgent
from lxml import etree
from func.const import *

class YouDao():
    """有道网页翻译"""
    def __init__(self,func):
        self.func = func

    async def get_resp(self,url):
        """获取有道源码"""
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Cookie": "OUTFOX_SEARCH_USER_ID_NCOO=1049708127.9005697",
            "Host": "webtrans.yodao.com",
            "Referer": "http://webtrans.yodao.com/webTransPc/index.html",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": UserAgent().random,
        }
        ips = self.func.get_lines(IPS_PATH)
        use_ip = random.choice(ips)
        # resp = await self.request_get(url, headers=headers, use_ip=use_ip,follow_redirects=True)
        resp = await self.func.request_get(url, headers=headers, use_ip=use_ip,follow_redirects=True)
        return resp

    async def web_trans(self,target_url):
        "网页翻译"
        o = str(int(time.time() * 1000) + random.randint(1, 10))
        r = "ydsecret://mdictweb.si/sign/-eV=8}L$s4$nPL00op3p]"
        t = target_url
        s = "mdictweb"
        c = s + o + r + t
        md5 = hashlib.md5()
        md5.update(c.encode("utf8"))
        c_md5 = md5.hexdigest()
        url = "http://webtrans.yodao.com/server/webtrans/tranUrl?url={}&from={}&to={}&type=1&product=mdictweb&salt={}&sign={}".format(t, 'auto', 'auto', o, c_md5)
        resp = await self.get_resp(url)
        source = resp.text.replace('&amp;','&')
        if '很抱歉，您输入的网址不存在或当前无法访问，请稍后重试' in source:
            return {'success':False}
        tree = etree.HTML(source)
        for i in tree.xpath('//a/@href'):
            if len(i.strip())>1:
                try:
                    url = i
                    s = re.search('url=(.*?)&from',url)
                    b = unquote(unquote(s.group(1)))
                    source = source.replace(i,b)
                except Exception as err:
                    print(i,err)
        source = re.sub('<base href=".*?">','',source)
        trans_from = re.search("TransFrom: '(.*?)'",source).group(1)
        trans_to = re.search("TransTo: '(.*?)'",source).group(1)
        source = re.sub(r"<script>var getParameter[\s\S]*</script>",'',source)
        return {'success':True,"from":trans_from,'to':trans_to,'source':source}
