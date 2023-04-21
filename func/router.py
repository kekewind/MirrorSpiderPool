# -*- coding: UTF-8 -*-
"""路由解析器"""

import json
import os
import random
import shutil
from collections import Counter
import time
import aiofiles
import arrow
from fastapi import FastAPI, Request, Response
from starlette.responses import JSONResponse, RedirectResponse
# from func.template import TemParser
from func.function import Func
from func.const import *
from func.spider import TargetSpider
from func.htmlParser import HtmlParser
from func.tagParser import TagParser


class Router():
    """路由解析器"""

    def __init__(self, templates):
        self.templates = templates
        # self.pool = pool
        self.func = Func()
        self.target = TargetSpider(self.func)
        self.parser = HtmlParser(self.func)
        os.makedirs(WEB_PATH, exist_ok=True)
        os.makedirs(TARGET_PATH, exist_ok=True)
        # os.makedirs(CACHE_TEM_PATH, exist_ok=True)
        # IP写入txt
        ips = self.func.get_ips()
        with open(IPS_PATH, 'w', encoding='utf-8')as txt_f:
            txt_f.write("\n".join(ips))

    async def api_verify(self, name, content):
        """生成站长验证代码"""
        if 10 < len(name) < 32 and 10 <= len(content) < 100:
            if not os.path.exists(VERIFY_PATH):
                os.makedirs(VERIFY_PATH)
            file_name = os.path.join(VERIFY_PATH, name)
            with open(file_name, 'w', encoding="utf-8") as txt_f:
                txt_f.write(content)
            return JSONResponse(status_code=200, content={"errcode": 0, "info": f"{name}文件已生成"})
        return JSONResponse(status_code=404, content={"errcode": 1, "info": "验证参数错误"})

    async def api_spider(self, mode):
        """api 蜘蛛数据"""
        now = arrow.now('Asia/Shanghai')
        if mode == '1d':
            all_spiders = {}
            for i in SPIDERS.keys():
                all_spiders[i] = 0
            for i in range(24):
                time_hour = now.shift(hours=-i).format('YYYY-MM-DD HH')
                log_dir_path = os.path.join(SPIDER_LOG, time_hour)
                spider_json_path = os.path.join(log_dir_path, "spider.json")
                spider_data = None
                if os.path.exists(log_dir_path):
                    # 查看是否存在spider.json文件
                    if not os.path.exists(spider_json_path):
                        # 生成json文件
                        if time_hour != now.format('YYYY-MM-DD HH'):
                            spider_data = await self.func.create_spider_json(log_dir_path)
                        else:
                            spider_data = await self.func.create_spider_json(log_dir_path, create_file=False)
                    else:
                        # 存在spider.json文件则直接用里面的数据
                        async with aiofiles.open(spider_json_path, 'r') as json_f:
                            json_text = await json_f.read()
                        spider_data = json.loads(json_text)
                # 汇总spider数据
                if spider_data is not None:
                    all_spiders_data = Counter(
                        all_spiders)+Counter(spider_data)
                    all_spiders = dict(all_spiders_data)
            result = {}
            for i in SPIDERS.keys():
                result[i] = 0
            result.update(all_spiders)
        elif mode == "24h":
            all_spiders = {}
            for i in range(24):
                time_hour = now.shift(hours=-i).format('YYYY-MM-DD HH')
                log_dir_path = os.path.join(SPIDER_LOG, time_hour)
                spider_json_path = os.path.join(log_dir_path, "spider.json")
                spider_data = None
                if os.path.exists(log_dir_path):
                    # 查看是否存在spider.json文件
                    if not os.path.exists(spider_json_path):
                        # 生成json文件
                        if time_hour != now.format('YYYY-MM-DD HH'):
                            spider_data = await self.func.create_spider_json(log_dir_path)
                        else:
                            spider_data = await self.func.create_spider_json(log_dir_path, create_file=False)
                    else:
                        # 存在spider.json文件则直接用里面的数据
                        async with aiofiles.open(spider_json_path, 'r') as json_f:
                            json_text = await json_f.read()
                        spider_data = json.loads(json_text)
                if spider_data is not None:
                    all_spiders[-i] = spider_data
            result = all_spiders
        return JSONResponse(status_code=200, content=result)

    def api_web_status(self, num):
        """api 网站状态"""
        send = os.popen(f"tail -{num} {ACCESS_LOG_PATH}")
        access = send.read().strip().split('\n')
        fuck = access[0].split(',')[0]
        cha_count = 1
        for index, i in enumerate(access):
            if fuck not in i:
                cha_count += index
                break
        re_access = access[::-1]
        fuck2 = re_access[0].split(',')[0]
        for index, i in enumerate(re_access):
            if fuck2 not in i:
                cha_count += index
                break
        count = len(access)-cha_count
        start_time = arrow.get(access[0].split(',')[0][1:]).timestamp()
        end_time = arrow.get(access[-1].split(',')[0][1:]).timestamp()
        spend_second = end_time-start_time-1
        qps = count/spend_second
        result = {"QPS": qps, "querry_count": count,
                  'spend_time': spend_second}
        return result

    async def template_list(self, request):
        """模板列表"""
        index_tems = sorted(os.listdir(INDEX_DIR))
        page_tems = sorted(os.listdir(PAGE_DIR))
        datas = {"request": request,
                 "urls": index_tems, "page_urls": page_tems}
        return self.templates.TemplateResponse(TEM_HTML, datas, media_type='text/html;charset=utf-8')

    async def sitemap(self, request, path=''):
        """网站地图"""
        url_path = str(request.url).replace(str(request.base_url), '')
        fuck = "abcdefghijklnmopqrstuvwxyz0123456789"
        if ".xml" in url_path:
            now = arrow.now('Asia/Shanghai')
            urls = [str(request.base_url)+"".join(random.choices(fuck, k=6))+".html"
                    for i in range(999)]
            times = [now.shift(hours=-random.randint(1, 24), seconds=-random.randint(
                1, 60), microseconds=-random.randint(1, 645888)) for i in range(999)]
            datas = {"request": request, "today": now.format(
                'YYYY-MM-DD'), 'time': str(now), 'urls': zip(urls, times)}
            return self.templates.TemplateResponse(SITEMAP_XML,
                                                   datas, media_type='text/xml')
        elif '.txt' in url_path:
            urls = [str(request.base_url)+"".join(random.choices(fuck, k=6))+".html"
                    for i in range(999)]
            datas = {"request": request, 'urls': urls}
            return self.templates.TemplateResponse(SITEMAP_TXT,
                                                   datas, media_type="text/plain")
        else:
            return RedirectResponse(url=f'sitemap{path}.xml', status_code=301)

    async def robots(self, request):
        """robots.txt 文件规定了搜索引擎抓取工具可以访问您网站上的哪些网址"""
        datas = {"request": request, }
        result = self.templates.TemplateResponse(
            ROBOTS_TXT, datas, media_type="text/plain")
        return result

    async def favicon(self):
        """网站图标"""
        async with aiofiles.open(FAVICON_PATH, 'rb')as image_f:
            target_tem = await image_f.read()
        return Response(content=target_tem, media_type='image/x-icon')

    async def route(self, request, response, path):
        """主路由"""
        # config = self.func.get_yaml(CONF_PATH)
        url = str(request.url)
        is_index = True if path == '' or path == '/' else False
        subdomain, full_domain, root_domain = self.func.get_domain_info(url)
        is_www = True if subdomain == 'www' or subdomain == '' else False
        web_yml_dir_path = os.path.join(WEB_PATH, root_domain)
        if is_www:
            web_yml_path = f'{web_yml_dir_path}.yml'
        else:
            web_yml_path = os.path.join(web_yml_dir_path, full_domain)+'.yml'
        url_path = full_domain+self.func.parse_path(path)+".json"
        print(url_path)
        web_json_dir_path = os.path.join(web_yml_dir_path,'cache')
        web_json_path = os.path.join(web_json_dir_path, url_path)
        # 判断是否存在配置文件
        if os.path.exists(web_yml_path):
            web_yml = self.func.get_yaml(web_yml_path)
        else:
            return web_yml_path+"不存在"
        target_url = web_yml["【镜像配置】"]["目标"]
        target_subdomain, target_full_domain, target_root_domain = self.func.get_domain_info(
            target_url)
        if is_index:
            target_dir_path = os.path.join(TARGET_PATH, target_full_domain)
            target_path = target_dir_path+"/index.html"
            target_tem_path = target_dir_path+"/from.yml"
        else:
            target_dir_path = os.path.join(
                TARGET_PATH, target_full_domain)+'/page/'
            target_url_path = target_full_domain+self.func.parse_path(path)
            target_path = os.path.join(target_dir_path, f'{target_url_path}')
            target_url = f"http://{target_full_domain}/{path.strip('./')}"
        if os.path.exists(target_path):
            if is_index:
                target_content, content_type = await self.target.linecache_get(target_path)
            else:
                target_content, content_type = await self.target.get(target_path)
        else:
            # mp4视频流处理
            if target_url[-len('.mp4'):] == '.mp4':
                print('流式处理视频')
                return RedirectResponse(url=f'/api/video?url={target_url}', status_code=301)
            os.makedirs(target_dir_path, exist_ok=True)
            # 爬取目标网址 缓存页面
            print('目标网址：', target_url)
            save_success = await self.target.save(target_url, target_path)
            if save_success:
                print(target_path, '保存成功')
                if is_index:
                    # tem配置文件路径写入
                    with open(target_tem_path, 'w', encoding='utf-8')as tem_f:
                        tem_f.write(f"path: {web_yml_path}")
                    target_content, content_type = await self.target.linecache_get(target_path)
                else:
                    target_content, content_type = await self.target.get(target_path)
            else:
                target_content = None
        if target_content is None:
            return Response(content=None, status_code=404)
        if "html" in content_type:
            # html 解析替换
            result = self.parser.replace(target_content, web_yml, is_index)
            # html 链接处理
            result = self.parser.link_change(result, root_domain, target_root_domain, target_full_domain)
            # html 标签处理
            if os.path.exists(web_json_path):
                async with aiofiles.open(web_json_path,'r')as json_f:
                    json_text = await json_f.read()
                replace_data = json.loads(json_text)['replace']
                for i in replace_data:
                    print(i)
                    result = result.replace(i[0],i[1])
            else:
                result,replace_data = TagParser(request,self.func).parse(result)
                if replace_data != []:
                    os.makedirs(web_json_dir_path, exist_ok=True)
                    json_data = {'domain':full_domain,
                                     'url':url,
                                     'create_time':int(time.time()),
                                     'replace':replace_data}
                    print(json_data)
                    json_dumps_str = json.dumps(json_data, ensure_ascii=False)
                    # 保存web json缓存
                    async with aiofiles.open(web_json_path,'w')as json_f:
                        await json_f.write(json_dumps_str)
        else:
            result = target_content
        return Response(content=result, media_type=content_type)
