# -*- coding: UTF-8 -*-
"""
《蜘蛛池》 by TG@seo888
"""

import aiomysql
import httpx
import uvicorn
from fastapi import FastAPI, Request, Response
from starlette.responses import JSONResponse, RedirectResponse,StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.gzip import GZipMiddleware
from starlette.templating import Jinja2Templates
from func.function import Func
from func import middle
from func.router import Router
from func.const import *

app = FastAPI()
# gzip流文件处理
app.add_middleware(GZipMiddleware, minimum_size=600)
# app.mount("/static", StaticFiles(directory="static"), name="static")
# func = Func()
# # 创建一个templates（模板）对象，以后可以重用。
templates = Jinja2Templates(directory=TEM_PATH)

@app.on_event("startup")
async def _startup():
#     """开机启动"""
#     # config = Func().get_yaml(CONF_PATH)
#     # host = config['【模板策略】']['云缓存SQL信息']['host']
#     # port = config['【模板策略】']['云缓存SQL信息']['port']
#     # user = config['【模板策略】']['云缓存SQL信息']['user']
#     # password = config['【模板策略】']['云缓存SQL信息']['password']
#     # dbname = config['【模板策略】']['云缓存SQL信息']['dbname']
#     # app.state.pool = await aiomysql.create_pool(
#     #     host=host, port=port, user=user, password=password, db=dbname,maxsize=65535
#     # )
#     # 路由引用
    app.state.router = Router(templates)

# @app.middleware("http")
# async def middleware(request: Request, call_next):
#     """中间件 访问前后"""
#     return await middle.middleware(request, call_next, func, templates)

@app.get("/api/video")
async def get_video(url: str):
    """api 生成站长验证代码"""
    async def iterfile():
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", url) as r:
                async for chunk in r.aiter_bytes():
                    yield chunk   
    return StreamingResponse(iterfile(), media_type="video/mp4")

@app.get("/api/verify")
async def verify(name: str, content: str):
    """api 生成站长验证代码"""
    return await app.state.router.api_verify(name, content)


@app.get("/api/spider")
async def spider(mode='1d'):
    """api 蜘蛛数据"""
    return await app.state.router.api_spider(mode)


@app.get("/api/web_status")
async def web_status(num: str = "50000"):
    """api 网站状态"""
    return app.state.router.api_web_status(num=int(num))


@app.get("/template_list")
async def template_list(request: Request):
    """模板列表"""
    return await app.state.router.template_list(request)


@app.get("/sitemap{path:path}.txt")
@app.get("/sitemap{path:path}.xml")
@app.get("/sitemap{path:path}.html")
async def sitemap(request: Request, path=''):
    """网站地图"""
    return await app.state.router.sitemap(request, path=path)


@app.get("/robots.txt")
async def robots(request: Request):
    """robots.txt 文件规定了搜索引擎抓取工具可以访问您网站上的哪些网址"""
    return await app.state.router.robots(request)


# @app.get("/favicon.ico")
# async def favicon():
#     """网站图标"""
#     return await app.state.router.favicon()


# @app.get("/")
# async def index(request: Request, response: Response):
#     """首页"""
#     # try:
#     #     result = await app.state.router.index(request, response, tem)
#     # except TypeError as error:
#     #     print(error)
#     #     result = JSONResponse(status_code=502, content={"error": '10003'})
#     # print(request.url)
#     result = await app.state.router.index(request, response)
    # return result


@app.get("{path:path}")
async def route(request: Request, response: Response, path=''):
    """主路由"""
    # print('path',path)
    # url = request
    # try:
    #     result = await app.state.router.page(request, response, path, tem)
    # except TypeError as error:
    #     print(error)
    #     result = JSONResponse(status_code=502, content={"error": '10004'})
    result = await app.state.router.route(request, response,path)
    return result



if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=16888)