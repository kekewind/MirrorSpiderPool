# -*- coding: UTF-8 -*-
"""目标站爬虫引擎"""

import json
import random
import httpx
import aiofiles
import chardet
from func.const import *
from func.htmlParser import HtmlParser

class TargetSpider():
    """目标站爬虫引擎"""

    def __init__(self,func):
        self.func = func
        self.parser = HtmlParser(self.func)

    async def get_resp(self,url):
        """获取目标站源码"""
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
        ips = self.func.get_lines(IPS_PATH)
        use_ip = random.choice(ips)
        resp = await self.func.request_get(url, headers=headers, use_ip=use_ip,follow_redirects=True)
        return resp

    def decode(self, result):
        """解码html源码"""
        try:
            result = result.decode(chardet.detect(result)['encoding'], "ignore")
        except:
            try:
                result = result.decode("utf-8", "ignore")
            except:
                try:
                    result = result.decode('gbk', "ignore")
                except:
                    try:
                        result = result.decode('gb2312', "ignore")
                    except:
                        result = result
        return result

    async def save(self,url,path,type_path):
        """保存缓存数据"""
        try:
            resp = await self.get_resp(url)
            try:
                media_type = resp.headers['Content-Type']
            except Exception as err:
                print(url,str(err))
                media_type = 'text/html'
            json_info = {"code":resp.status_code,"media_type":media_type}
            async with aiofiles.open(type_path,'w',encoding='utf-8')as json_f:
                await json_f.write(json.dumps(json_info))
            # 写入内容
            if json_info['code']==200:
                # 清洁源码
                if 'text' in json_info['media_type']:
                    resp_text = self.decode(resp.content)
                    # 保存前清洁
                    result = self.parser.clean(resp_text)
                    async with aiofiles.open(path,'w')as cache_f:
                        await cache_f.write(result)
                else:
                    async with aiofiles.open(path,'wb')as cache_f:
                        await cache_f.write(resp.content)
            return True
        except Exception as err:
            print(f"{path} save error:",err)
            return False

    async def get(self,path,type_path):
        """获取缓存数据"""
        async with aiofiles.open(type_path,'r')as json_f:
            json_content = await json_f.read()
        json_info = json.loads(json_content)
        content = None
        content_type = json_info['media_type']
        if json_info['code']==200:
            if 'html' in content_type:
                async with aiofiles.open(path,'r')as content_f:
                    content = await content_f.read()
            else:
                async with aiofiles.open(path,'rb')as content_f:
                    content = await content_f.read()
        # 处理重复charset=utf-8;
        content_type = content_type.replace("charset=utf-8",'').strip('; ')
        return content,content_type
    
    async def linecache_get(self,path,type_path):
        """获取缓存数据 内存模式"""
        json_content = self.func.get_text(type_path)
        json_info = json.loads(json_content)
        content = None
        if json_info['code']==200:
            content = self.func.get_text(path)
        content_type = json_info['media_type']
        # 处理重复charset=utf-8;
        content_type = content_type.replace("charset=utf-8",'').strip('; ')
        return content,content_type
    
