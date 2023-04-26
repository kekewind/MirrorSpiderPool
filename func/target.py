# -*- coding: UTF-8 -*-
"""目标站爬虫引擎"""

import json
import random
import os
import time
import httpx
import aiofiles
import chardet
from func.const import *
from func.htmlParser import HtmlParser

class Target():
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

    async def save(self,config,url,target_dir,path,type_path):
        """保存缓存数据"""
        try:
            # 请求处理前计时
            start_time = time.time()
            resp = await self.get_resp(url)
            # 请求处理后
            x_request_time = time.time() - start_time
            try:
                media_type = resp.headers['Content-Type']
            except Exception as err:
                print(url,str(err))
                media_type = 'text/html'
            # 写入内容
            if resp.status_code==200:
                # 清洁源码
                if 'text' in media_type:
                    # 保存文本文件
                    resp_text = self.decode(resp.content)
                    # 保存前清洁
                    result = self.parser.clean(resp_text)
                    if len(resp_text.strip())>0:
                        async with aiofiles.open(path,'w')as cache_f:
                            await cache_f.write(result)
                        if 'htm' in media_type and '/page/' in target_dir:
                            # 写入sitemap.txt
                            sitemap = os.path.join(target_dir.replace('/page/',''),'sitemap.txt')
                            async with aiofiles.open(sitemap,'a',encoding='utf-8')as txt_f:
                                await txt_f.write(path+"\n")
                else:
                    # 保存二进制文件
                    async with aiofiles.open(path,'wb')as cache_f:
                        await cache_f.write(resp.content)
                    # jpg反转
                    if config['【目标站缓存】']['开启缓存图片翻转'] and any([path[-len(i):]==i for i in ['.jpg','.jpeg','.png','.gif']]):
                        self.func.flip_image(path)
                json_info = {"code":resp.status_code,"media_type":media_type}
                # 写入type文件
                async with aiofiles.open(type_path,'w',encoding='utf-8')as json_f:
                    await json_f.write(json.dumps(json_info))
                return True,x_request_time
            else:
                json_info = {"code":resp.status_code,"media_type":media_type}
                # 写入type文件
                async with aiofiles.open(type_path,'w',encoding='utf-8')as json_f:
                    await json_f.write(json.dumps(json_info))
                return False,x_request_time
        except Exception as err:
            print(f"{path} save error: {str(err)}")
            return False,0

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