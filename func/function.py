# -*- coding: UTF-8 -*-
"""功能函数"""

from socket import gethostbyname
import linecache
import html
import os
import gzip
import json
import random
import sys
from urllib.parse import quote,unquote
import aiofiles
from zhconv import convert
from PIL import Image
import tldextract
import jiagu
import httpx
from ruamel.yaml import YAML
from func.const import *


class Func():
    """功能函数"""

    def __init__(self):
        self.yaml=YAML()
        self.yaml.default_flow_style = False
        self.yaml.indent(mapping=2, sequence=4, offset=2)
        self.errcode = self.get_yaml(ERRCODE_PATH)

    async def request_get(self, url, headers=None, params=None,follow_redirects=True, use_ip='0.0.0.0'):
        """异步访问 GET"""
        transport = httpx.AsyncHTTPTransport(local_address=use_ip)
        async with httpx.AsyncClient(http2=False, transport=transport) as client:
            resp = await client.get(url, headers=headers, params=params,follow_redirects=follow_redirects,timeout=15)
        return resp

    async def request_post(self, url, headers=None, params=None, datas=None, use_ip='0.0.0.0'):
        """异步访问 POST"""
        transport = httpx.AsyncHTTPTransport(local_address=use_ip)
        async with httpx.AsyncClient(http2=False, transport=transport) as client:
            resp = await client.post(url, headers=headers, params=params, json=datas,timeout=15)
        return resp
    
    async def request_stream(self, url, headers=None, params=None,follow_redirects=True, use_ip='0.0.0.0'):
        """异步访问 GET流式"""
        transport = httpx.AsyncHTTPTransport(local_address=use_ip)
        async with httpx.AsyncClient(http2=False, transport=transport) as client:
            try:
                async with client.stream("GET", url,headers=headers, params=params,follow_redirects=follow_redirects,timeout=15) as r:
                    async for chunk in r.aiter_bytes():
                        yield chunk
            except Exception as err:
                print('异步访问 GET流式 报错：',url,str(err))

    def get_ips(self):
        """获取当前服务器所有IP"""
        nowsys = sys.platform
        if 'win' in nowsys:
            return []
        try:
            ips_list = os.popen('ip addr').readlines()
            ips = []
            for i in ips_list:
                if "inet " in i:
                    i = i.strip().split(' ')[1].split('/')[0]
                    ips.append(i)
            if "127.0.0.1" in ips:
                ips.remove('127.0.0.1')
            return ips
        except Exception as err:
            print(err)
            return []

    def exists_chinese(self,string):
        """判断字符串中是否存在中文"""
        for i in string:
            if u'\u4e00' <= i <= u'\u9fff':
                return True
        return False

    def is_url(self,url):
        """判断url是否是网址"""
        tld = tldextract.extract(url)
        domain = ".".join([tld.domain, tld.suffix]).lower()
        if domain[-1] == '.':
            return False
        return True

    def get_domain_info(self, domain):
        """获取域名前后缀"""
        tld = tldextract.extract(domain)
        subdomain = tld.subdomain.lower()
        full_domain = ".".join(
            [tld.subdomain, tld.domain, tld.suffix]).strip(".").lower()
        root_domain = ".".join([tld.domain, tld.suffix]).strip(".").lower()
        return subdomain, full_domain, root_domain

    def get_yaml(self, path):
        """解析yaml文件"""
        linecache.checkcache(path)
        yml = "".join(linecache.getlines(path))
        result = self.yaml.load(yml)
        return result
    
    def save_yaml(self,path,data):
        """保存yaml文件"""
        with open(path, "w", encoding="utf-8") as yml_f:
            self.yaml.dump(data, yml_f)

    async def save_gz(self,data,path):
        """保存gzip压缩文件"""
        async with aiofiles.open(path, 'wb') as gz_f:
            # 压缩数据
            data_comp = gzip.compress(data.encode())
            await gz_f.write(data_comp)

    def get_text(self, path):
        """文本文件解析"""
        linecache.checkcache(path)
        text = "".join(linecache.getlines(path))
        return text

    def get_lines(self, path):
        """txt文件解析"""
        linecache.checkcache(path)
        result = list(set([i.strip() for i in linecache.getlines(path)]))
        if '' in result:
            result.remove('')
        return result

    def transcoding(self, string):
        """html实体化转码"""
        new = ""
        for i in string:
            if '\u4e00' <= i <= '\u9fff':
                new += "&#" + str(ord(i)) + ";"
            else:
                new += i
        return new
    
    def unescape(self,string):
        """html实体解码"""
        return html.unescape(string)

    def to_hant(self,string):
        """简体转繁体"""
        return convert(string, 'zh-hant')

    async def get_file_count(self, file_path):
        """快速获取文档行数"""
        return sum(1 for _ in open(file_path))

    async def create_spider_json(self, log_dir_path, create_file=True):
        """生成spider.json文件"""
        spider_data = {}
        for i in SPIDERS.keys():
            spider_data[i] = 0
        # 生成json文件
        for i in os.listdir(log_dir_path):
            log_path = os.path.join(log_dir_path, i)
            count = await self.get_file_count(log_path)
            spider_data[i[:-4]] += count
        if create_file:
            spider_json_path = os.path.join(log_dir_path, "spider.json")
            async with aiofiles.open(spider_json_path, 'w') as json_f:
                await json_f.write(json.dumps(spider_data, sort_keys=True, indent=4))
        return spider_data
    
    def flip_image(self, picpath):
        """翻转图片"""
        im = Image.open(picpath)
        new_pic = im.transpose(Image.FLIP_LEFT_RIGHT)
        new_pic.save(picpath)
        print(f"图片翻转成功 {picpath}")

    def get_text_keyword(self, text, k=1):
        """文本关键词抽取"""
        keywords = []
        for i in jiagu.keywords(text, 50):
            i = i.strip('. ,')
            if len(i) > 1 and not i.isdigit():
                keywords.append(i)
        if len(keywords) < k:
            k = len(keywords)
        keys = random.sample(keywords, k=k)
        return keys

    def url_get_path(self, url):
        """url文件路径解析"""
        domain = self.get_domain_info(url)[-1]
        if url[:len('http://')] == "http://":
            url = url[len('http://'):]
        if url[:len('https://')] == "https://":
            url = url[len('https://'):]
        url = quote(url.strip('./'))
        while "./" in url:
            url = url.replace('./', "/").strip('./')
        while "//" in url:
            url = url.replace('//', "/").strip('./')
        dir_ = os.path.dirname(url)
        base_name = os.path.basename(url)
        dir_path = os.path.join(os.path.join(CACHE_PATH, domain), dir_)
        file_path = os.path.join(dir_path, base_name+".cache")
        return file_path, dir_path

    def clean_url(self, url):
        """url路径解析"""
        sub, full_domain, domain = self.get_domain_info(url)
        if url[:len('http://')] == "http://":
            url = url[len('http://'):]
        if url[:len('https://')] == "https://":
            url = url[len('https://'):]
        url = quote(url.strip('./'))
        while "./" in url:
            url = url.replace('./', "/").strip('./')
        while "//" in url:
            url = url.replace('//', "/").strip('./')
        url = f"http://{url}"
        return url, sub, full_domain, domain

    async def get_sql_cache(self, pool, url):
        """获取sql缓存"""
        link = self.clean_url(url)[0]
        result = None
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    sql_command = f"SELECT cache FROM spider_pool WHERE link='{link}' LIMIT 1"
                    await cur.execute(sql_command)
                    await conn.commit()
                    result = await cur.fetchone()
                    if result is not None:
                        result = result[0]
                        # 数量+1
                        sql_command = f"update spider_pool set request_count=request_count+1 WHERE link='{link}'"
                        await cur.execute(sql_command)
                        await conn.commit()
                except Exception as err:
                    print(err)
        return result

    async def save_sql_cache(self, pool, url, content, title, is_index, tem_name):
        """保存sql缓存"""
        link, sub, full_domain, domain = self.clean_url(url)
        if sub == "" or sub == "www":
            url_type = "主站"
        else:
            url_type = "泛站"
        page_type = "首页" if is_index else "内页"
        data = (domain, full_domain, link, content,
                title, url_type, page_type, 1, tem_name)
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                sql_command = f"INSERT INTO spider_pool(domain,full_domain,link,cache,title,type,page_type,request_count,template) VALUE{str(data)};"
                try:
                    await cur.execute(sql_command)
                    await conn.commit()
                except Exception as err:
                    # print(err)
                    if "doesn't exist" in str(err):
                        # 开始创建字段
                        sql_command = """CREATE TABLE spider_pool(
id INT NOT NULL AUTO_INCREMENT,
domain VARCHAR(100) NOT NULL,
full_domain VARCHAR(100) NOT NULL,
link VARCHAR(500) NOT NULL,
cache LONGTEXT NOT NULL,
title VARCHAR(200),
template VARCHAR(100),
type VARCHAR(10) NOT NULL,
page_type VARCHAR(10) NOT NULL,
create_time timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP,
update_time timestamp(0) NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP(0),
request_count int(100) DEFAULT NULL,
PRIMARY KEY ( id ),
UNIQUE (link)
);"""
                        await cur.execute(sql_command)
                        await conn.commit()

    async def get_cache(self, url):
        """获取本地缓存文件"""
        file_path = self.url_get_path(url)[0]
        content = None
        if os.path.exists(file_path):
            async with aiofiles.open(file_path, 'r', encoding='utf-8')as cache_f:
                content = await cache_f.read()
        return content

    async def save_cache_tem(self, url, content):
        """保存缓存"""
        file_path, dir_path = self.url_get_path(url)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        async with aiofiles.open(file_path, 'w', encoding='utf-8')as cache_f:
            await cache_f.write(content)

    def loading_ad_meta(self, tem, is_index, show_tem=''):
        """处理JS广告 verify验证文件"""
        if show_tem == '':
            config = self.get_yaml(CONF_PATH)
            jsad = "\n".join(config['【JS广告】'])+"\n"
            tem = tem.replace('</head>', jsad+"</head>")
        # 加verify验证文件
        if is_index:
            meta_tags = []
            for name in os.listdir(VERIFY_PATH):
                verify_file_path = os.path.join(VERIFY_PATH, name)
                linecache.checkcache(verify_file_path)
                content = "".join(linecache.getlines(verify_file_path)).strip()
                meta_tag = f'<meta name="{name}" content="{content}">'
                meta_tags.append(meta_tag)
            if len(meta_tags) > 0:
                meta = "\n".join(meta_tags)
                tem = tem.replace('</head>', meta+"\n</head>")
        return tem

    async def get_sql_tem(self, pool, link):
        """获取sql缓存"""
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    sql_command = f"SELECT template FROM spider_pool WHERE link='{link}' LIMIT 1"
                    await cur.execute(sql_command)
                    await conn.commit()
                    result = await cur.fetchone()
                    # print(result)
                    if result is not None:
                        result = result[0]
                        if result is None:
                            result = ""
                    else:
                        result = None
                except Exception as err:
                    print(err)
                    result = 'error'
        return result

    async def save_sql_tem(self, pool, link, tem_name):
        """保存sql tem 缓存"""
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    # 数量+1
                    sql_command = f"update spider_pool set template='{tem_name}' WHERE link='{link}'"
                    await cur.execute(sql_command)
                    await conn.commit()
                except Exception as err:
                    print(err)

    async def get_tem_cache(self, pool, base_url, tem_name, is_index, config):
        """获取当前url的引用模板路径"""
        link, sub, full_domain, domain = self.clean_url(base_url)
        create_index_page = False
        if config['【模板策略】']['云缓存']:
            result = await self.get_sql_tem(pool, link)
            if result == '':
                # 存在link 但没有template 开始 update 新的模板
                await self.save_sql_tem(pool, link, tem_name)
            elif result is None:
                # 不存在首页link
                create_index_page = True
            elif result == 'error':
                # 连接数据库报错 不知道存不存在link
                pass
            else:
                tem_name = result
        else:
            cache_tem_file_dir = os.path.join(CACHE_TEM_PATH, domain)
            os.makedirs(cache_tem_file_dir, exist_ok=True)
            cache_tem_file_path = os.path.join(
                cache_tem_file_dir, full_domain+".yml")
            if not os.path.exists(cache_tem_file_path):
                yml_content = f"name: '{tem_name}'"
                # 写入引用模板名
                async with aiofiles.open(cache_tem_file_path, 'w', encoding='utf-8')as yml_f:
                    await yml_f.write(yml_content)
            cache_tem = self.get_yaml(cache_tem_file_path)
            tem_name = cache_tem['name']
        if is_index:
            tem_path = os.path.join(INDEX_DIR, tem_name)
            if not os.path.exists(tem_path):
                tem_path = os.path.join(PAGE_DIR, tem_name)
        else:
            tem_path = os.path.join(PAGE_DIR, tem_name)
        return tem_path, tem_name, create_index_page
    
    def parse_path(self,url_path):
        """解析url_path"""
        # url反攻击处理
        while "//" in url_path or './' in url_path:
            url_path = url_path.replace('//','/').replace('./','/')
        path = url_path.strip('./').replace('/','\\')
        path = "\\"+quote(path).replace('%5C','\\')
        path = '' if path == '\\' else path
        return path
