# -*- coding: UTF-8 -*-
"""gunicorn后台运行"""

import os
import re
import time
import click


def createj_nginx_conf(port):
    "自动创建nginx配置文件"
    if not os.path.exists("logs"):
        os.makedirs("./logs")
    path = "/www/server/panel/vhost/nginx/SpiderPool.conf"
    if os.path.exists(path):
        with open(path, "r", encoding='utf8') as f:
            conf = f.read()
        print(f"nignx配置信息：\n{conf}")
    else:
        conf = """server
{
    listen 80;
    server_name _;
    index index.html;
    root /www/server/nginx/html;
    location / {
        proxy_pass http://127.0.0.1:【端口号】;
        proxy_pass_header Server;
        proxy_redirect off;
        proxy_set_header X-Real-IP $remote_addr; #后端的Web服务器可以通过X-Forwarded-For获取用户真实IP
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        #以下是一些反向代理的配置,可选.
        proxy_set_header Host $host;
        client_max_body_size 10m; #允许客户端请求的最大单文件字节数
        client_body_buffer_size 128k; #缓冲区代理缓冲用户端请求的最大字节数,
        proxy_connect_timeout 90; #nginx跟后端服务器连接超时时间(代理连接超时)
        proxy_send_timeout 90; #后端服务器数据回传时间(代理发送超时)
        proxy_read_timeout 90; #连接成功后,后端服务器响应时间(代理接收超时)
        proxy_buffer_size 4k; #设置代理服务器（nginx）保存用户头信息的缓冲区大小
        proxy_buffers 4 32k; #proxy_buffers缓冲区,网页平均在32k以下的设置
        proxy_busy_buffers_size 64k; #高负荷下缓冲大小（proxy_buffers*2）
        proxy_temp_file_write_size 64k;
        #设定缓存文件夹大小,大于这个值,将从upstream服务器传
    }
    # 定义错误页面码，如果出现相应的错误页面码，转发到那里。
    error_page  500 502 503 504  /50x.html;
    # 承接上面的location。
    location = /50x.html {
    # 放错误页面的目录路径。当然默认可以在网站目录下，也可以定义放置错误页面的位置。
        root   /www/wwwroot/SpiderPool/template/others;
    }
}""".replace("【端口号】", port)
        with open(path, "w", encoding='utf8') as f:
            f.write(conf)


def start():
    "开始"
    port = "16888"
    createj_nginx_conf(port)
    content = "gunicorn -c conf.py main:app -k uvicorn.workers.UvicornWorker --daemon"
    os.popen(content)
    print('程序已运行')


def close():
    "关闭"
    send = os.popen("pstree -ap|grep gunicorn")
    result = send.read()
    if "|-gunicorn," in result:
        print('程序后台运行中，正在关闭进程...')
        program_name = os.path.basename(os.path.abspath('.'))
        sid = re.findall(r'gunicorn,(\d+) .*?/'+program_name, result)
        print(sid)
        for i in sid:
            kill = f"kill -9 {i}"
            print(kill+f" from {program_name}")
            os.system(kill)


def restart():
    "重启"
    close()
    print('现在启动程序')
    time.sleep(1)
    start()


@click.command()
@click.option("--mode", default="0", help="模式：1.重启 2.停止 ")
def run(mode):
    """运行"""
    if mode == "0":
        mode = input('0.启动 1.重启 2.停止 选择模式：')
    if mode == "0":
        start()
    elif mode == "1":
        restart()
    else:
        close()


if __name__ == '__main__':
    run()
