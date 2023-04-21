# -*- coding: UTF-8 -*-

import configparser
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import os, sys
import multiprocessing
from gunicorn.glogging import Logger

class CustomLogger(Logger):
    """Custom logger for Gunicorn log messages."""

    def setup(self, cfg):
        """Configure Gunicorn application logging configuration."""
        super().setup(cfg)
        self._set_handler(self.error_log, cfg.errorlog, logging.Formatter(fmt=("[%(asctime)s] %(levelname)s | %(message)s")))
        self._set_handler(self.access_log, cfg.accesslog, logging.Formatter(fmt=("[%(asctime)s] %(levelname)s | %(message)s")))

x_forwarded_for_header = "X-Real-IP"
bind = '0.0.0.0:16888'
workers = multiprocessing.cpu_count() * 2 + 1  # 并行工作进程数
worker_class = 'uvicron.workers.UvicornWorker'  # 还可以使用gevent模式，还可以使用sync模式，默认sync模式
threads = multiprocessing.cpu_count() * 2  # 指定每个工作者的线程数
backlog = 2048  # 监听队列
timeout = 30  # 超过多少秒后工作将被杀掉，并重新启动。一般设置为30秒或更多
worker_connections = 65535 # 设置最大并发量
max_requests = 65535
daemon = False  # 默认False，设置守护进程，将进程交给supervisor管理
debug = False
loglevel = 'info'
proc_name = 'main'  # 默认None，这会影响ps和top。如果要运行多个Gunicorn实例，需要设置一个名称来区分，这就要安装setproctitle模块。如果未安装
accesslog = './logs/access.log'
pidfile = './logs/gunicron.pid'  # 设置进程文件目录
errorlog = './logs/error.log'
preload_app = True  # 预加载资源
autorestart = True
logger_class = CustomLogger