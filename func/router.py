# -*- coding: UTF-8 -*-
"""路由解析器"""

import json
import os
import random
import shutil
from urllib.parse import unquote
from collections import Counter
import time
import aiofiles
import arrow
from fastapi import FastAPI, Request, Response
from fake_useragent import UserAgent
from starlette.responses import JSONResponse, RedirectResponse, StreamingResponse,FileResponse
from func.function import Func
from func.const import *
from func.target import Target
from func.htmlParser import HtmlParser
from func.tagParser import TagParser


class Router():
    """路由解析器"""

    def __init__(self,executor, templates):
        self.executor = executor
        self.templates = templates
        self.func = Func()
        self.target = Target(executor,self.func)
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

    async def tem(self,request,show):
        """api tem模板展示"""
        template = os.path.join(TEMPLATE_DIR,show)
        if os.path.exists(template):
            result = self.func.get_text(template)
            result = TagParser(request, self.func).parse(result)[0]
            return Response(content=result, media_type="text/html")

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
        if os.path.exists(ACCESS_LOG_PATH):
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
        else:
            return {'不存在日志文件':ACCESS_LOG_PATH}
        return result

    async def template_list(self, request):
        """模板列表"""
        tems = sorted(os.listdir(TEMPLATE_DIR))
        datas = {"request": request,
                 "urls": [], "page_urls": tems}
        return self.templates.TemplateResponse(TEM_HTML, datas, media_type='text/html;charset=utf-8')

    async def sitemap(self, request, path=''):
        """网站地图"""
        config = self.func.get_yaml(CONF_PATH)
        url = str(request.url)
        subdomain, full_domain, root_domain = self.func.get_domain_info(url)
        is_main = True if subdomain == 'www' or subdomain == '' else False
        web_yml_dir_path = os.path.join(WEB_PATH, root_domain)
        # web缓存文件目录
        web_cache_dir_path = os.path.join(web_yml_dir_path, 'cache')
        # web配置文件路径
        if is_main:
            web_yml_path = f'{web_yml_dir_path}.yml'
        else:
            web_yml_path = os.path.join(web_yml_dir_path, full_domain)+'.yml'
        # 判断是否存在web配置文件
        if os.path.exists(web_yml_path):
            web_yml = self.func.get_yaml(web_yml_path)
        else:
            # 没有则创建新的web yml配置文件
            return self.create_web_yml(request, config, is_main, web_cache_dir_path,web_yml_path)
        target_url = web_yml["【镜像配置】"]["目标"]
        target_full_domain = self.func.get_domain_info(target_url)[1]
        target_dir_path = os.path.join(TARGET_PATH, target_full_domain)
        target_sitemap_path = os.path.join(target_dir_path,'sitemap.txt')
        target_pages =[unquote(str(request.base_url).strip('/')+i.split(f'page/{target_full_domain}',1)[1].replace('\\','/')) for i in self.func.get_lines(target_sitemap_path)]
        target_pages_count = len(target_pages)

        url_path = str(request.url).replace(str(request.base_url), '')
        fuck = "abcdefghijklnmopqrstuvwxyz0123456789"

        if ".xml" in url_path:
            now = arrow.now('Asia/Shanghai')
            urls = target_pages+[str(request.base_url)+"".join(random.choices(fuck, k=6))+".html"
                    for i in range(999)]
            times = [now.shift(hours=-random.randint(1, 24), seconds=-random.randint(
                1, 60), microseconds=-random.randint(1, 645888)) for i in range(999+target_pages_count)]
            datas = {"request": request, "today": now.format(
                'YYYY-MM-DD'), 'time': str(now), 'urls': zip(urls, times)}
            return self.templates.TemplateResponse(SITEMAP_XML,datas, media_type='text/xml')
        elif '.txt' in url_path:
            urls = target_pages+[str(request.base_url)+"".join(random.choices(fuck, k=6))+".html"
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

    async def status_404(self,request, config,real_url_path,web_yml,target_dir_path,root_domain, target_root_domain, target_full_domain,web_gz_path):
        """主路由404页面处理"""
        if not config['【泛目录设置】']['开启泛目录功能']:
            return Response(content=None, status_code=404)
        save_cache = False if config['【蜘蛛池设置】']['开启动态蜘蛛池'] else True
        template = web_yml['【镜像配置】']['模板']
        is_static = True if any([real_url_path[-len(i):] == i for i in MEDIA_TYPE_LIST]) else False
        if template == '自动':
            # 随机引用当前网站的目标站内页
            target_sitemap_path = os.path.join(target_dir_path.replace('/page/',''),'sitemap.txt')
            if os.path.exists(target_sitemap_path):
                if len(target_pages := self.func.get_lines(target_sitemap_path))>0:
                    target_tem_path = random.choice(target_pages)
                    async with aiofiles.open(target_tem_path,'r',encoding='utf-8')as f:
                        target_tem = await f.read()
                    
                    # html 解析替换
                    result = self.parser.replace(target_tem, web_yml, False)
                    # html 链接处理 动态蜘蛛处理
                    cut_num = config['【泛目录设置】']['自动模板链接转换比例']
                    img_num = config['【泛目录设置】']['自动模板图片转换比例']
                    result = self.parser.dynamic_link_change(config, result, root_domain, target_root_domain, target_full_domain,cut_num=cut_num,img_num=img_num)
                    # 标签替换
                    result = TagParser(request, self.func).parse(result)[0]
                    if save_cache and not is_static:
                        await self.func.save_gz(result,web_gz_path)
                    return Response(content=result, media_type="text/html")
        else:
            print(template)
            if os.path.exists(template):
                result = self.func.get_text(template)
                result = TagParser(request, self.func).parse(result)[0]
                if save_cache and not is_static:
                    await self.func.save_gz(result,web_gz_path)
                return Response(content=result, media_type="text/html")
            else:
                return JSONResponse(status_code=404, content={"errcode": "10003", "info": self.func.errcode['10003']})

    def save_web_yml(self, tag, father_yml_path, web_yml_path, mode='copy'):
        """保存web_yml配置文件"""
        try:
            base_yml = self.func.get_yaml(BASE_YML_PATH)
            yml = self.func.get_yaml(father_yml_path)
            if mode == 'copy':
                yml_json = {'域名': yml['【镜像配置】']['域名'],
                            '目标': yml['【镜像配置】']['目标'],
                            '核心词': yml['【镜像配置】']['核心词'],
                            '模板': yml['【镜像配置】']['模板'],
                            '标题': yml['【首页TDK】']['标题'],
                            '关键词': yml['【首页TDK】']['关键词'],
                            '描述': yml['【首页TDK】']['描述']}
            else:
                yml_json = {'域名': base_yml['【镜像配置】']['域名'],
                            '目标': yml['【镜像配置】']['目标'],
                            '核心词': base_yml['【镜像配置】']['核心词'],
                            '模板': base_yml['【镜像配置】']['模板'],
                            '标题': base_yml['【首页TDK】']['标题'],
                            '关键词': base_yml['【首页TDK】']['关键词'],
                            '描述': base_yml['【首页TDK】']['描述']}
            yml_json_str = json.dumps(yml_json, ensure_ascii=False)
            result = tag.parse(yml_json_str[1:-1])[0]
            yml_json = json.loads("{"+result+"}")
            yml['【镜像配置】']['域名'] = yml_json['域名']
            yml['【镜像配置】']['核心词'] = yml_json['核心词']
            yml['【镜像配置】']['目标'] = yml_json['目标']
            yml['【镜像配置】']['模板'] = yml_json['模板'].lstrip('/')
            yml['【首页TDK】']['标题'] = yml_json['标题']
            yml['【首页TDK】']['关键词'] = yml_json['关键词']
            yml['【首页TDK】']['描述'] = yml_json['描述']
            self.func.save_yaml(web_yml_path, yml)
        except Exception as err:
            print(f'保存{web_yml_path} 失败', str(err))

    def create_web_yml(self, request, config, is_main,web_cache_dir_path, web_yml_path):
        """创建web配置"""
        if (is_main and config['【自动化设置】']['自动主站']) or (not is_main and config['【自动化设置】']['自动泛站']):
            if is_main:
                father_yml_path = config['【自动化设置】']['主站配置模板']
            else:
                father_yml_path = config['【自动化设置】']['泛站配置模板']
            tag = TagParser(request, self.func)
            os.makedirs(web_cache_dir_path,exist_ok=True)
            if father_yml_path == "自动":
                # 配置模板 随机抽取现有目标站的from.yml
                target_list = os.listdir(TARGET_PATH)
                if len(target_list) <= 5:
                    return JSONResponse(status_code=404, content={"errcode": "10002", "info": self.func.errcode['10002']})
                target = random.choice(target_list)
                from_yml = os.path.join(TARGET_PATH, f'{target}/from.yml')
                father_yml_path = self.func.get_yaml(from_yml)['path']
                self.save_web_yml(tag, father_yml_path,web_yml_path, mode='from')
            else:
                self.save_web_yml(tag, father_yml_path, web_yml_path)
            redirect_url = str(request.url).split(str(request.base_url), 1)[1]
            redirect_url = '/' if redirect_url == '' else redirect_url
            return RedirectResponse(url=redirect_url, status_code=301)
        else:
            return JSONResponse(status_code=404, content={"errcode": "10001", "info": self.func.errcode['10001']})

    async def get_target_content(self, config, is_index, path,target_dir_path, target_path,target_url, web_yml_path):
        """获取目标站数据"""
        target_type_path = target_path+'.type'
        if os.path.exists(target_path):
            print(f'存在目标站缓存：{target_path}')
            if is_index:
                target_content, content_type = await self.target.linecache_get(target_path, target_type_path)
            else:
                target_content, content_type = await self.target.get(target_path, target_type_path)
            # 存在缓存 直接返回
            return {'success': True, 'content': target_content, 'type': content_type,"X-Request-Time":0}
        elif os.path.exists(target_type_path):
            # 存在type文件
            print(f'不存在目标站缓存 但存在type：{target_type_path}')
            async with aiofiles.open(target_type_path, 'r')as json_f:
                json_content = await json_f.read()
            json_info = json.loads(json_content)
            if json_info['code'] != 200:
                return {'success': False, "info": "状态码非200", "code": json_info['code'], 'type': json_info['media_type']}
            print(f'缓存被删除 重新获取目标站缓存 {target_path}')
        else:
            print(f'不存在目标站缓存与type 获取目标站缓存：{target_path}')

        # 判断是否需要缓存
        if not config['【目标站缓存】']['开启缓存']:
            print(f'缓存功能已关闭 跳过缓存目标站 {target_path}')
            return {'success': False, "info": "缓存功能已关闭"}

        # 静态文件流处理
        if config['【目标站缓存】']['开启静态文件缓存']:
            media_type_list = [i for i in MEDIA_TYPE.keys(
            ) if i not in config['【目标站缓存】']['缓存静态文件名']]
        else:
            media_type_list = list(MEDIA_TYPE.keys())
        if any(path[-len(i):] == i for i in media_type_list):
            # 跳转到文件流处理
            return {'success': False,"info": "跳转到文件流处理", "jump": f'/-/{target_url.replace("http://","").replace("https://","")}'}

        os.makedirs(target_dir_path, exist_ok=True)

        if not any([path[-len(i):] == i for i in config['【目标站缓存】']['缓存静态文件名']]):
            # 判断是否达到目标站页面缓存上限
            if config['【目标站缓存】']['缓存页面上限']==0:
                return {'success': False, "info": "缓存上限为0 禁止缓存"}
            else:
                target_sitemap_path = os.path.join(target_dir_path.replace('/page/',''),'sitemap.txt')
                if os.path.exists(target_sitemap_path):
                    target_page_count = len(self.func.get_lines(target_sitemap_path))
                    if target_page_count>=config['【目标站缓存】']['缓存页面上限']:
                        return {'success': False, "info": f"缓存上限达到{config['【目标站缓存】']['缓存页面上限']} 禁止缓存"}

        print('爬取目标网址：', target_url)
        # 爬取目标网址 缓存页面
        save_success,request_time = await self.target.save(config,target_url, target_dir_path,target_path, target_type_path)
        if not save_success:
            return {'success': False, "info": "数据保存失败"}
        print(target_path, '保存成功')
        if is_index:
            # 如果是首页访问 新开目标站 则在from.yml中写入配置文件路径web_yml_path
            target_from_path = target_dir_path+"/from.yml"
            async with aiofiles.open(target_from_path, 'w', encoding='utf-8')as tem_f:
                await tem_f.write(f"path: {web_yml_path}")
            target_content, content_type = await self.target.linecache_get(target_path, target_type_path)
        else:
            target_content, content_type = await self.target.get(target_path, target_type_path)
        return {'success': True, 'content': target_content, 'type': content_type,'X-Request-Time':request_time}

    async def route(self, request, response, path):
        """主路由"""
        config = self.func.get_yaml(CONF_PATH)
        url = str(request.url)
        subdomain, full_domain, root_domain = self.func.get_domain_info(url)
        is_main = True if subdomain == 'www' or subdomain == '' else False
        web_yml_dir_path = os.path.join(WEB_PATH, root_domain)
        # web缓存文件目录
        web_cache_dir_path = os.path.join(web_yml_dir_path, 'cache')
        # web 泛目录缓存文件名 .gz
        real_path = url.split(root_domain, 1)[1]
        url_gz_path = full_domain+self.func.parse_path(real_path)+".gz"
        # web 泛目录缓存文件路径 .gz
        web_gz_path = os.path.join(web_cache_dir_path, url_gz_path)
        # 判断是否存在gz 泛目录缓存 存在则直接返回 gz 文件
        if config['【泛目录设置】']['开启泛目录功能'] and os.path.exists(web_gz_path):
            resp = FileResponse(web_gz_path,media_type='text/html')
            print('直接返回gz文件')
            resp.headers[ 'Content-Encoding'] = 'gzip'
            resp.headers["X-Gz"] = '1'
            return resp
        
        # web配置文件路径
        if is_main:
            web_yml_path = f'{web_yml_dir_path}.yml'
        else:
            web_yml_path = os.path.join(web_yml_dir_path, full_domain)+'.yml'

        # 判断是否存在web配置文件
        if os.path.exists(web_yml_path):
            web_yml = self.func.get_yaml(web_yml_path)
        else:
            # 没有则创建新的web yml配置文件
            return self.create_web_yml(request, config, is_main, web_cache_dir_path,web_yml_path)
        target_url = web_yml["【镜像配置】"]["目标"]
        target_subdomain, target_full_domain, target_root_domain = self.func.get_domain_info(target_url)
        is_index = True if path == '' or path == '/' else False
        # web缓存文件名
        url_path = full_domain+self.func.parse_path(real_path)+".json"
        # web缓存文件路径
        web_json_path = os.path.join(web_cache_dir_path, url_path)
        
        if is_index:
            target_dir_path = os.path.join(TARGET_PATH, target_full_domain)
            # 首页 目标站缓存文件路径
            target_path = target_dir_path+"/index.html"
        else:
            target_dir_path = os.path.join(TARGET_PATH, target_full_domain)+'/page/'
            # 内页 目标站缓存文件名
            target_url_path = target_full_domain + \
                self.func.parse_path(real_path)
            # 内页 目标站缓存文件路径
            target_path = os.path.join(target_dir_path, f'{target_url_path}')
            # 内页 目标站网址
            target_url = f"http://{target_full_domain}/{real_path.strip('./')}"

        # 首页 等待访问的目标站网址
        target_result = await self.get_target_content(config, is_index, path,target_dir_path, target_path,target_url, web_yml_path)
        if not target_result['success']:
            if 'jump' in target_result:
                # 跳转到文件流处理
                return RedirectResponse(url=target_result['jump'], status_code=301)
            print(target_result['info'])
            return await self.status_404(request, config,path,web_yml,target_dir_path,root_domain, target_root_domain, target_full_domain,web_gz_path)
            # if 'code' in target_result:
            #     return Response(content=str(target_result['code']), media_type=target_result['type'], status_code=target_result['code'])
            # return Response(content=None, status_code=404)
        target_content, content_type = target_result['content'], target_result['type']
        # response.headers["X-Request-Time"] = str(target_result['X-Request-Time'])
        if "html" not in content_type:
            resp = Response(content=target_content, media_type=content_type)
            resp.headers["X-Request-Time"] = str(target_result['X-Request-Time'])
            # 非html页面直接返回
            return resp

        # 动态模式 镜像页动态处理
        if config['【蜘蛛池设置】']['开启动态蜘蛛池']:
            # html 解析替换
            result = self.parser.replace(target_content, web_yml, is_index)
            # html 链接处理 动态蜘蛛处理
            cut_num = config['【蜘蛛池设置】']['镜像页链接转换比例']
            img_num = config['【泛目录设置】']['自动模板图片转换比例']
            result = self.parser.dynamic_link_change(config, result, root_domain, target_root_domain, target_full_domain,cut_num=cut_num,img_num=img_num)
            # 动态蜘蛛池模式 已经拿到目标站缓存数据
            result = TagParser(request, self.func).parse(result)[0]
            # 动态蜘蛛池 直接返回动态数据
            print('蜘蛛池模式进了')
            resp = Response(content=result, media_type=content_type)
            resp.headers["X-Request-Time"] = str(target_result['X-Request-Time'])
            return resp

        # html 解析替换
        result = self.parser.replace(target_content, web_yml, is_index)
        # html 链接处理
        result = self.parser.link_change(
            result, root_domain, target_root_domain, target_full_domain)
        # web json缓存处理
        if os.path.exists(web_json_path):
            # 读取web json缓存
            async with aiofiles.open(web_json_path, 'r')as json_f:
                json_text = await json_f.read()
            replace_data = json.loads(json_text)['replace']
            # html 标签处理替换
            for i in replace_data:
                result = result.replace(i[0], i[1],1)
        else:
            # 不存在缓存 开始生成缓存文件
            result, replace_data = TagParser(request, self.func).parse(result)
            if replace_data != []:
                os.makedirs(web_cache_dir_path, exist_ok=True)
                json_data = {'domain': full_domain,
                             'url': url,
                             'target_url': target_url,
                             'target_path': target_path,
                             'create_time': int(time.time()),
                             'replace': replace_data}
                # print(json_data)
                json_dumps_str = json.dumps(json_data, ensure_ascii=False)
                # 保存web json缓存
                async with aiofiles.open(web_json_path, 'w')as json_f:
                    await json_f.write(json_dumps_str)
        resp = Response(content=result, media_type=content_type)
        resp.headers["X-Request-Time"] = str(target_result['X-Request-Time'])
        return resp

    async def stream(self, path):
        """流式代理访问目标站静态文件"""
        if self.func.is_url(path):
            media_type = None
            url = f'http://{path}'
            for i in list(MEDIA_TYPE.keys()):
                if path[-len(i):] == i:
                    ips = self.func.get_lines(IPS_PATH)
                    use_ip = random.choice(ips)
                    headers = {'User-Agent': UserAgent().random}
                    print('流式代理:', url)
                    media_type = MEDIA_TYPE[i]
                    break
            if media_type is not None:
                try:
                    stream_resp = self.func.request_stream(url, headers=headers, use_ip=use_ip)
                except Exception as err:
                    print('流式访问：',path,str(err))
                    return Response(content=None, status_code=404)
                return StreamingResponse(stream_resp, media_type=media_type)
        return Response(content=None, status_code=404)
