# -*- coding: UTF-8 -*-
"""中间件 访问前后"""

import time
import os
import linecache
import aiofiles
from starlette.responses import JSONResponse, RedirectResponse
from starlette.templating import Jinja2Templates
import tldextract
import arrow
from func.const import *


async def middleware(request, call_next, func, templates):
    """中间件 访问前后"""
    # 请求处理前计时
    start_time = time.time()
    config = func.get_yaml(CONF_PATH)
    print(str(request.url))
    subdomain, full_domain, root_domain = func.get_domain_info(str(request.url))
    # 是否开放IP直接访问
    if not config['【访问策略】']['开放IP与非域名访问']:
        if root_domain.replace('.', '').isdigit():
            return JSONResponse(status_code=403, content={"禁止直接访问IP": root_domain})
        if "." not in root_domain and full_domain != "spiderpool":
            return JSONResponse(status_code=403, content={"禁止非法访问": full_domain})
    # UA黑名单处理
    if 'user-agent' not in request.headers:
        return JSONResponse(status_code=403, content={"error": '10005'})
    res_ua = request.headers['user-agent']
    fuck_uas = config["【访问策略】"]["UA黑名单"]
    if fuck_uas != '' and any(i in res_ua for i in fuck_uas.split("|")):
        return JSONResponse(status_code=403, content={"error": '10002'})
    # IP黑名单处理
    res_ip = request.headers['x-real-ip']
    fuck_ips = config["【访问策略】"]["IP黑名单"]
    if fuck_ips != '' and any(i in res_ip for i in fuck_ips.split("|")):
        return JSONResponse(status_code=403, content={"error": '10001'})
    # 拦截根域名 跳WWW
    if config['【访问策略】']['根域名跳WWW']:
        full_domain, root_domain = func.get_domain_info(str(request.base_url))[1:]
        if full_domain == root_domain:
            new_url = str(request.url).replace(
                'http://', "http://www.").replace('https://', "https://www.")
            return RedirectResponse(url=new_url, status_code=301)
    url_path = str(request.url).replace(str(request.base_url), '')
    real_url_path = url_path.split('?', maxsplit=1)[0]
    is_user = False
    is_static = True if any([real_url_path[-len(i):] == i for i in MEDIA_TYPE_LIST]) else False
    # 写入本地蜘蛛日志
    if config["【蜘蛛设置】"]['开启蜘蛛日志']:
        now = arrow.now('Asia/Shanghai')
        spider_log_path = os.path.join(SPIDER_LOG, now.format('YYYY-MM-DD HH'))
        if not os.path.exists(spider_log_path):
            try:
                os.makedirs(spider_log_path)
                # 上一小时生成spider.json
                last_spider_log_path = os.path.join(
                    SPIDER_LOG, now.shift(hours=-1).format('YYYY-MM-DD HH'))
                await func.create_spider_json(last_spider_log_path)
            except Exception:
                pass
        for spider_name, spider_tag in SPIDERS.items():
            if spider_tag in res_ua:
                if spider_name == '普通用户':
                    is_user = True
                elif is_static:
                    if config["【蜘蛛设置】"]['开启蜘蛛日志'] == 0:
                        # 触发蜘蛛静态资源访问屏蔽
                        return JSONResponse(status_code=403, content={"静态资源访问禁止": str(request.url), "UA": res_ua})
                    elif config["【蜘蛛设置】"]['开启蜘蛛日志'] == 2:
                        # 触发蜘蛛静态资源开放但不录入日志
                        break
                # 解析yaml配置文件
                if config["【蜘蛛设置】"]['蜘蛛开关'][spider_name]:
                    line = str(now)+" | "+res_ua+" | " + \
                        str(request.url)+" | "+res_ip
                    file_path = os.path.join(
                        spider_log_path, spider_name)+'.txt'
                    async with aiofiles.open(file_path, 'a', encoding='utf-8')as log_f:
                        await log_f.write(line+"\n")
                    break
                else:
                    # 触发蜘蛛开关屏蔽
                    return JSONResponse(status_code=403, content={"UA禁止": res_ua})
    # 广告直跳 普通用户直跳广告
    if config["【访问策略】"]['普通用户直跳广告'] and is_user and "api/" not in real_url_path and "static/" not in real_url_path:
        datas = {"request": request}
        return templates.TemplateResponse(AD_HTML, datas, media_type='text/html;charset=utf-8')
    # 广告直跳 搜索来路直跳广告
    if config["【访问策略】"]['搜索来路直跳广告'] and is_user and not is_static:
        # 获取referer
        if 'referer' in request.headers:
            referer = request.headers['referer']
            if any(i in referer for i in
                   ["baidu.com/", "google.com/", 'bing.com/', 'sogou.com/', 'so.com/']):
                datas = {"request": request}
                return templates.TemplateResponse(AD_HTML, datas, media_type='text/html;charset=utf-8')
    # ---------------
    response = await call_next(request)
    # ---------------
    # 请求处理后
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    # response.headers["X-From"] = config['【网站信息】']['程序名称']
    return response