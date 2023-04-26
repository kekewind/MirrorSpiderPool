# -*- coding: UTF-8 -*-
"""html源码解析器"""

import re
import random
from lxml import etree


class HtmlParser():
    """html源码解析器"""

    def __init__(self, func):
        self.func = func

    def clean(self, source):
        """源码清洁"""
        # 格式化 html标签
        source = re.sub('<html[\s\S]*?>', '<html>', source, flags=re.I)
        source = re.sub('</html>', '</html>', source, flags=re.I)
        # 格式化 head标签
        source = re.sub('<head[\s\S]*?>', '<head>', source, flags=re.I)
        source = re.sub('</head>', '</head>', source, flags=re.I)
        # 格式化 body标签
        source = re.sub('<body[\s\S]*?>', '<body>', source, flags=re.I)
        source = re.sub('</body>', '</body>', source, flags=re.I)
        # <head>标签丢失检测
        if "<head>" not in source:
            source = source.replace('<html>', '<html>\n<head>', 1)
        if "</head>" not in source:
            source = source.replace('<body>', '</head>\n<body>', 1)
        # 过滤所有<!--.*?-->的备注信息
        source = re.sub('<!-[\s\S]*?-->', '', source)
        # 处理特殊title
        source = source.replace('title =', 'title=')
        # 替换charset
        source = re.sub('charset=".*?"', 'charset="utf-8"', source, flags=re.I)
        source = source.replace('gb2312"', 'utf-8"')
        # 过滤谷歌认证代码
        source = re.sub(r'<meta name="google.*?>', "", source, flags=re.I)
        # 过滤noscript
        source = re.sub(
            r"<noscript>[\s\S]*?</noscript>", "", source, flags=re.I)
        # 匹配所有JS，过滤谷歌JS
        all_js = re.findall(
            r"<script[\s\S]*?>[\s\S]*?</script>", source, flags=re.I)
        for js_code in all_js:
            if any([i in js_code for i in ['google', 'elgoog', 'facebook', 'koobecaf', 'cnzz.com', 'baidu.com', '51.la']]):
                source = source.replace(js_code, "")
        # 去回车
        source = "\n".join([i for i in source.strip().split('\n') if len(i.strip()) > 0])
        # 实体解码
        source = self.func.unescape(source)
        return source

    def index_repalce(self, source, conf):
        """首页替换处理"""
        title = conf["【首页TDK】"]['标题']
        des = conf["【首页TDK】"]['描述']
        keywords = conf["【首页TDK】"]['关键词']
        core_word = conf["【镜像配置】"]['核心词']
        replace_line = conf["【首页替换】"]["单行替换"]
        replace_lines = conf["【首页替换】"]["多行替换"]
        global_replace_line = conf["【全局替换】"]["单行替换"]
        global_replace_lines = conf["【全局替换】"]["多行替换"]
        # 核心词标签处理
        # title = title.replace('{核心词}', core_word)
        # des = des.replace('{核心词}', core_word)
        # keywords = keywords.replace('{核心词}', core_word)
        # replace_lines = replace_lines.replace('{核心词}', core_word)
        # replace_line = [i.replace('{核心词}', core_word) for i in replace_line]
        # global_replace_lines = global_replace_lines.replace('{核心词}', core_word)
        # global_replace_line = [
        #     i.replace('{核心词}', core_word) for i in global_replace_line]
        # 过滤TDK
        if des is not None and len(des) > 1:
            # 转码处理
            if conf["【首页TDK】"]['转码'] and '{' not in des:
                des = self.func.transcoding(des)
            print(des)
            # 删除description
            source = re.sub(r'<meta.*?name="Description".*?/>',
                            "", source, flags=re.I)
            source = re.sub(r"<meta.*?name='Description'.*?/>",
                            "", source, flags=re.I)
            # 写入description
            source = source.replace(
                '<head>', f'<head>\n<meta name="description" content="{des}" />')
        if keywords  is not None and len(keywords) > 1:
            # 转码处理
            if conf["【首页TDK】"]['转码'] and '{' not in keywords:
                keywords = self.func.transcoding(keywords)
            # 删除keywords
            source = re.sub(r'<meta.*?name="Keywords".*?/>',
                            "", source, flags=re.I)
            source = re.sub(r"<meta.*?name='Keywords'.*?/>",
                            "", source, flags=re.I)
            # 写入keywords
            source = source.replace(
                '<head>', f'<head>\n<meta name="keywords" content="{keywords}" />')
        if title is not None and len(title) > 1:
            # 转码处理
            if conf["【首页TDK】"]['转码'] and '{' not in title:
                title = self.func.transcoding(title)
            # 删除title
            source = re.sub(r"<title[\s\S]*?</title>", "", source, flags=re.I)
            # 写入title
            source = source.replace(
                '<head>', f'<head>\n<title>{title}</title>')
        # 单行替换
        for i in replace_line:
            if '----------' in i and '##########' in i:
                # -#替换格式兼容
                for line in i.split('##########'):
                    if len(line_list:=line.split('----------'))==2:
                        try:
                            source = source.replace(line_list[0], line_list[1])
                        except Exception as err:
                            print(i, str(err))
            elif len(line := i.split(" -> ", 1)) == 2:
                try:
                    source = source.replace(line[0], line[1])
                except Exception as err:
                    print(i, str(err))
            else:
                print(i, '替换格式错误')
        # 多行替换
        for i in re.findall('r`([\s\S]*?)``([\s\S]*?)`', replace_lines):
            source = re.sub(i[0], i[1], source)
        for i in re.findall('r`[\s\S]*?``[\s\S]*?`', replace_lines):
            replace_lines = replace_lines.replace(i, '')
        for i in re.findall('`([\s\S]*?)``([\s\S]*?)`', replace_lines):
            source = source.replace(i[0], i[1])
        # 全局单行替换
        for i in global_replace_line:
            if '----------' in i and '##########' in i:
                # -#替换格式兼容
                for line in i.split('##########'):
                    if len(line_list:=line.split('----------'))==2:
                        try:
                            source = source.replace(line_list[0], line_list[1])
                        except Exception as err:
                            print(i, str(err))
            elif len(line := i.split(" -> ", 1)) == 2:
                try:
                    source = source.replace(line[0], line[1])
                except Exception as err:
                    print(i, str(err))
            else:
                print(i, '替换格式错误')
        # 全局多行替换
        for i in re.findall('r`([\s\S]*?)``([\s\S]*?)`', global_replace_lines):
            source = re.sub(i[0], i[1], source)
        for i in re.findall('r`[\s\S]*?``[\s\S]*?`', global_replace_lines):
            global_replace_lines = global_replace_lines.replace(i, '')
        for i in re.findall('`([\s\S]*?)``([\s\S]*?)`', global_replace_lines):
            source = source.replace(i[0], i[1])
        return source

    def page_repalce(self, source, conf):
        """首页替换处理"""
        title = conf["【内页TDK】"]['标题']
        des = conf["【内页TDK】"]['描述']
        keywords = conf["【内页TDK】"]['关键词']
        core_word = conf["【镜像配置】"]['核心词']
        replace_line = conf["【内页替换】"]["单行替换"]
        replace_lines = conf["【内页替换】"]["多行替换"]
        global_replace_line = conf["【全局替换】"]["单行替换"]
        global_replace_lines = conf["【全局替换】"]["多行替换"]
        # 过滤TDK
        if des is not None and len(des) > 1:
            # 转码处理
            if conf["【首页TDK】"]['转码'] and '{' not in des:
                des = self.func.transcoding(des)
            print(des)
            # 删除description
            source = re.sub('<meta.*?name="Description".*?/>',
                            "", source, flags=re.I)
            source = re.sub("<meta.*?name='Description'.*?/>",
                            "", source, flags=re.I)
            # 写入description
            source = source.replace(
                '<head>', f'<head>\n<meta name="description" content="{des}" />')
        if keywords  is not None and len(keywords) > 1:
            # 转码处理
            if conf["【首页TDK】"]['转码'] and '{' not in keywords:
                keywords = self.func.transcoding(keywords)
            # 删除keywords
            source = re.sub(r'<meta.*?name="Keywords".*?/>',
                            "", source, flags=re.I)
            source = re.sub(r"<meta.*?name='Keywords'.*?/>",
                            "", source, flags=re.I)
            # 写入keywords
            source = source.replace(
                '<head>', f'<head>\n<meta name="keywords" content="{keywords}" />')
        if title is not None and len(title) > 1:
            # 转码处理
            if conf["【首页TDK】"]['转码'] and '{' not in title:
                title = self.func.transcoding(title)
            # 删除title
            source = re.sub(r"<title[\s\S]*?</title>", "", source, flags=re.I)
            # 写入title
            source = source.replace(
                '<head>', f'<head>\n<title>{title}</title>')
        # 单行替换
        for i in replace_line:
            if '----------' in i and '##########' in i:
                # -#替换格式兼容
                for line in i.split('##########'):
                    if len(line_list:=line.split('----------'))==2:
                        try:
                            source = source.replace(line_list[0], line_list[1])
                        except Exception as err:
                            print(i, str(err))
            elif len(line := i.split(" -> ", 1)) == 2:
                try:
                    source = source.replace(line[0], line[1])
                except Exception as err:
                    print(i, str(err))
            else:
                print(i, '替换格式错误')
        # 多行替换
        for i in re.findall('r`([\s\S]*?)``([\s\S]*?)`', replace_lines):
            source = re.sub(i[0], i[1], source)
        for i in re.findall('r`[\s\S]*?``[\s\S]*?`', replace_lines):
            replace_lines = replace_lines.replace(i, '')
        for i in re.findall('`([\s\S]*?)``([\s\S]*?)`', replace_lines):
            source = source.replace(i[0], i[1])
        # 全局单行替换
        for i in global_replace_line:
            if '----------' in i and '##########' in i:
                # -#替换格式兼容
                for line in i.split('##########'):
                    if len(line_list:=line.split('----------'))==2:
                        try:
                            source = source.replace(line_list[0], line_list[1])
                        except Exception as err:
                            print(i, str(err))
            elif len(line := i.split(" -> ", 1)) == 2:
                try:
                    source = source.replace(line[0], line[1])
                except Exception as err:
                    print(i, str(err))
            else:
                print(i, '替换格式错误')
        # 全局多行替换
        for i in re.findall('r`([\s\S]*?)``([\s\S]*?)`', global_replace_lines):
            source = re.sub(i[0], i[1], source)
        for i in re.findall('r`[\s\S]*?``[\s\S]*?`', global_replace_lines):
            global_replace_lines = global_replace_lines.replace(i, '')
        for i in re.findall('`([\s\S]*?)``([\s\S]*?)`', global_replace_lines):
            source = source.replace(i[0], i[1])
        return source

    def replace(self, source, conf, is_index):
        """替换生成"""
        if is_index:
            source = self.index_repalce(source, conf)
        else:
            source = self.page_repalce(source, conf)
        return source

    def link_change(self, source, my_root_domain, target_root_domain, target_full_domain):
        """链接处理"""
        # 　link链接处理
        tree = etree.HTML(source)
        links = tree.xpath("//link/@href")
        for link in links:
            if any(link[:len(i)] == i for i in ['http://', "https://", '//']):
                link_subdomain, link_full_domain, link_root_domain = self.func.get_domain_info(
                    link)
                if link_full_domain == target_full_domain:
                    # 目标网址转本站相对路径
                    new_link_path = link.split(target_full_domain, 1)[1]
                    new_link = new_link_path if new_link_path != '' else '/'
                    source = source.replace(f'href="{link}"', f'href="{new_link}"').replace(
                        f"href='{link}'", f'href="{new_link}"')
                elif link_root_domain == target_root_domain:
                    # 目标泛站网址处理为自己的泛站
                    link_split = link.split(target_root_domain, 1)
                    new_link = link_split[0].replace(
                        'http://', '//').replace('https://', '//')+my_root_domain+link_split[1]
                    source = source.replace(f'href="{link}"', f'href="{new_link}"').replace(
                        f"href='{link}'", f'href="{new_link}"')
        # 　a链接处理
        a_links = tree.xpath("//a/@href")
        for link in a_links:
            # 处理所有绝对链接
            if any(link[:len(i)] == i for i in ['http://', "https://", '//']):
                link_subdomain, link_full_domain, link_root_domain = self.func.get_domain_info(
                    link)
                if link_full_domain == target_full_domain:
                    # 目标网址转本站相对路径
                    new_link_path = link.split(target_full_domain, 1)[1]
                    new_link = new_link_path if new_link_path != '' else '/'
                elif link_root_domain == target_root_domain:
                    # 目标泛站网址处理为自己的泛站
                    link_split = link.split(target_root_domain, 1)
                    new_link = link_split[0].replace(
                        'http://', '//').replace('https://', '//')+my_root_domain+link_split[1]
                else:
                    # 外链处理
                    new_link = '{外链}'
                source = source.replace(f'href="{link}"', f'href="{new_link}"').replace(
                    f"href='{link}'", f'href="{new_link}"')
            elif link == '#' or link == '':
                new_link = '{外链}'
                source = source.replace(f'href="{link}"', f'href="{new_link}"').replace(
                    f"href='{link}'", f'href="{new_link}"')
        # src处理
        src_list = re.findall("src='(.*?)'", source) + \
            re.findall('src="(.*?)"', source)
        for link in src_list:
            if any(link[:len(i)] == i for i in ['http://', "https://", '//']):
                link_subdomain, link_full_domain, link_root_domain = self.func.get_domain_info(
                    link)
                if link_full_domain == target_full_domain:
                    # 目标网址转本站相对路径
                    new_link_path = link.split(target_full_domain, 1)[1]
                    new_link = new_link_path if new_link_path != '' else '/'
                    source = source.replace(f'src="{link}"', f'src="{new_link}"').replace(
                        f"src='{link}'", f'src="{new_link}"')
                elif link_root_domain == target_root_domain:
                    # 目标泛站网址处理为自己的泛站
                    link_split = link.split(target_root_domain, 1)
                    new_link = link_split[0].replace(
                        'http://', '//').replace('https://', '//')+my_root_domain+link_split[1]
                    source = source.replace(f'src="{link}"', f'src="{new_link}"').replace(
                        f"src='{link}'", f'src="{new_link}"')
        return source

    def dynamic_link_change(self, config, source, my_root_domain, target_root_domain, target_full_domain,cut_num=None,img_num=None):
        """链接处理 蜘蛛池动态处理"""
        # 　link链接处理
        tree = etree.HTML(source)
        links = tree.xpath("//link/@href")
        for link in links:
            if any(link[:len(i)] == i for i in ['http://', "https://", '//']):
                link_full_domain, link_root_domain = self.func.get_domain_info(link)[
                    1:]
                if link_full_domain == target_full_domain:
                    # 目标网址转本站相对路径
                    new_link_path = link.split(target_full_domain, 1)[1]
                    new_link = new_link_path if new_link_path != '' else '/'
                    source = source.replace(f'href="{link}"', f'href="{new_link}"').replace(
                        f"href='{link}'", f'href="{new_link}"')
                elif link_root_domain == target_root_domain:
                    # 目标泛站网址处理为自己的泛站
                    link_split = link.split(target_root_domain, 1)
                    new_link = link_split[0].replace(
                        'http://', '//').replace('https://', '//')+my_root_domain+link_split[1]
                    source = source.replace(f'href="{link}"', f'href="{new_link}"').replace(
                        f"href='{link}'", f'href="{new_link}"')
        # 　a链接处理
        a_links = tree.xpath("//a/@href")
        for link in a_links:
            # 处理所有绝对链接
            if any(link[:len(i)] == i for i in ['http://', "https://", '//']):
                link_full_domain, link_root_domain = self.func.get_domain_info(link)[1:]
                if link_full_domain == target_full_domain:
                    # 目标网址转本站相对路径
                    new_link_path = link.split(target_full_domain, 1)[1]
                    new_link = new_link_path if new_link_path != '' else '/'
                    source = source.replace(f'href="{link}"', f'href="{new_link}"').replace(f"href='{link}'", f'href="{new_link}"')
                elif link_root_domain == target_root_domain:
                    # 目标泛站网址处理为自己的泛站
                    link_split = link.split(target_root_domain, 1)
                    new_link = link_split[0].replace(
                        'http://', '//').replace('https://', '//')+my_root_domain+link_split[1]
                    source = source.replace(f'href="{link}"', f'href="{new_link}"').replace(f"href='{link}'", f'href="{new_link}"')        
        tree = etree.HTML(source)
        # 　a链接处理
        a_dict = {'内链': [], '外链': [], "泛站": [], '泛站内链': []}
        for i in tree.xpath("//a"):
            link = link[0] if len(link := i.xpath('@href')) > 0 else ''
            a_text = a_text[0] if len(a_text := i.xpath('text()')) > 0 else ''
            # print(link, a_text)
            if "javascript:" in link:
                continue
            # 处理所有绝对链接
            if any(link[:len(i)] == i for i in ['http://', "https://", '//']):
                link_full_domain, link_root_domain = self.func.get_domain_info(link)[
                    1:]
                if link_full_domain == target_full_domain:
                    a_dict['内链'].append((a_text,link))
                elif link_root_domain == target_root_domain:
                    a_dict["泛站内链"].append((a_text,link))
                else:
                    # 外链处理
                    a_dict['外链'].append((a_text,link))
            elif link in ('#', ''):
                a_dict['泛站'].append((a_text,link))
            else:
                a_dict['内链'].append((a_text,link))
        
        random.shuffle(a_dict['内链'])
        random.shuffle(a_dict['外链'])
        random.shuffle(a_dict['泛站'])
        random.shuffle(a_dict['泛站内链'])
        if cut_num!=1:
            new_a_dict = {
                '内链': a_dict['内链'][:int(len(a_dict['内链'])*cut_num)],
                '外链': a_dict['外链'][:int(len(a_dict['外链'])*cut_num)],
                '泛站': a_dict['泛站'][:int(len(a_dict['泛站'])*cut_num)],
                '泛站内链': a_dict['泛站内链'][:int(len(a_dict['泛站内链'])*cut_num)]
            }
        else:
            new_a_dict = a_dict
        # 链接占比重新分配
        per_dict = config['【泛目录设置】']['自动模板链接占比']
        count_list = [per_dict['内链'],per_dict['外链'],per_dict['泛站'],per_dict['泛站内链']]
        sum_count = sum(count_list)
        new_link_dict = {'内链': [], '外链': [], "泛站": [], '泛站内链': []}
        if sum_count != 0:
            # 重新分配链接占比
            link_count = sum([len(links) for links in new_a_dict.values()])
            outside_count = int(link_count*(per_dict['外链']/sum_count))
            web_count = int(link_count*(per_dict['泛站']/sum_count))
            web_inside_count = int(link_count*(per_dict['泛站内链']/sum_count))
            all_links = new_a_dict['内链']+new_a_dict['外链']+new_a_dict['泛站内链']+new_a_dict['泛站']
            for i in range(web_count):
                link = all_links.pop()
                new_link_dict['泛站'].append(link)
            for i in range(web_inside_count):
                link = all_links.pop()
                new_link_dict['泛站内链'].append(link)
            for i in range(outside_count):
                link = all_links.pop()
                new_link_dict['外链'].append(link)
            new_link_dict['内链'] = all_links
            new_a_dict = new_link_dict

        print(new_a_dict)
        for k,links in new_a_dict.items():
            print(k,len(links))
            for a_text,link in links:
                new_link = "{"+k+"}"
                if link!='/':
                    source = source.replace(f'href="{link}"', f'href="{new_link}"').replace(f"href='{link}'", f'href="{new_link}"')
                if len(a_text)>7:
                    source = source.replace(f'>{a_text}</a>',">{标题}</a>")
        # src处理
        src_list = re.findall("src='(.*?)'", source, flags=re.I) + \
            re.findall('src="(.*?)"', source, flags=re.I)
        for link in src_list:
            if any(link[:len(i)] == i for i in ['http://', "https://", '//']):
                link_full_domain, link_root_domain = self.func.get_domain_info(link)[
                    1:]
                if link_full_domain == target_full_domain:
                    # 目标网址转本站相对路径
                    new_link_path = link.split(target_full_domain, 1)[1]
                    new_link = new_link_path if new_link_path != '' else '/'
                    source = source.replace(f'src="{link}"', f'src="{new_link}"').replace(
                        f"src='{link}'", f'src="{new_link}"')
                elif link_root_domain == target_root_domain:
                    # 目标泛站网址处理为自己的泛站
                    link_split = link.split(target_root_domain, 1)
                    new_link = link_split[0].replace(
                        'http://', '//').replace('https://', '//')+my_root_domain+link_split[1]
                    source = source.replace(f'src="{link}"', f'src="{new_link}"').replace(
                        f"src='{link}'", f'src="{new_link}"')
        # title属性删除
        title_list = re.findall("title='(.*?)'", source, flags=re.I) + \
            re.findall('title="(.*?)"', source, flags=re.I)
        for title in title_list:
            source = source.replace(f'title="{title}"', '').replace(
                f"title='{title}'", '')
        tree = etree.HTML(source)
        # h标签文章处理
        title_count = 0
        for i in ['h1','h2','h3','h4']:
            tags = tree.xpath(f"//{i}/text()")
            for tag in tags:
                if "{" not in tag and self.func.exists_chinese(tag):
                    if len(tag.strip())>7:
                        if title_count==0:
                            source = source.replace(f">{tag}<",'>{title}<')
                            print('title',tag)
                            title_count +=1
                        else:
                            source = source.replace(f">{tag}<",'>{标题}<')
        # 标签文章处理
        for i in ['p','span','div']:
            tags = tree.xpath(f"//{i}//text()")
            for tag in tags:
                if "{" not in tag and self.func.exists_chinese(tag):
                    if 25>=len(tag.strip())>7:
                        if title_count==0:
                            source = source.replace(f">{tag}<",'>{title}<')
                            print('title',tag)
                            title_count +=1
                        else:
                            source = source.replace(f">{tag}<",'>{标题}<')
                    elif len(tag.strip())>25:
                        source = source.replace(f">{tag}<",'>{句子({keyword},0-1)}<')
        # 图片链接处理
        if len(img_srcs:= tree.xpath("//img/@src"))>0:
            random.shuffle(img_srcs)
            for link in img_srcs[:int(len(img_srcs)*img_num)]:
                source = source.replace(f'src="{link}"', 'src="{随机图片}"').replace(
                        f"src='{link}'", 'src="{随机图片}"')
        return source
