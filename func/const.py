# -*- coding: UTF-8 -*-
"""常量配置"""

SPIDERS = {
    "百度蜘蛛": "aidu",
    "搜狗蜘蛛": "Sogou",
    "神马蜘蛛": "Yisou",
    "头条蜘蛛": "Bytespider",
    "必应蜘蛛": "Bingbot",
    "360蜘蛛": "360Spider",
    "谷歌图片蜘蛛": "Googlebot-Image",
    "谷歌蜘蛛": "Googlebot",
    "雅虎蜘蛛": "Yahoo",
    "其它蜘蛛": "spider",
    "其他蜘蛛": "bot",
    "普通用户": "",
}

TRANS_LANG = {
    '中文': 'zh-cn',
    '英文': 'en',
    '日文': 'ja',
}

MEDIA_TYPE = {
    '.jpg':'image/jpeg'
}

CONF_PATH = "config/config.yml"
TAG_PATH = "config/tag.yml"
IPS_PATH = "config/IPS.txt"
VERIFY_PATH = 'config/verify/'
TEM_PATH = "template"
TEM_HTML = "others/templates.html"
AD_HTML = "others/ad.html"
SITEMAP_XML = "others/sitemap.xml"
SITEMAP_TXT = "others/sitemap.txt"
ROBOTS_TXT = "others/robots.txt"
INDEX_DIR = "template/index/"
PAGE_DIR = "template/page/"
FAVICON_PATH = "static/_/image/favicon.ico"
SPIDER_LOG = "logs/spider"
CACHE_PATH = 'cache/'
CACHE_TEM_PATH = 'cache_tem/'
ACCESS_LOG_PATH = 'logs/access.log'

WEB_PATH = 'web'
TARGET_PATH = 'target'
