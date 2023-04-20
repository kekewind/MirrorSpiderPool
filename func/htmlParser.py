# -*- coding: UTF-8 -*-
"""html源码解析器"""

import re


class HtmlParser():
    """html源码解析器"""
    def __init__(self,func):
        self.func = func

    def clean(self,source):
        """源码清洁"""
        # 格式化 html标签
        source = re.sub('<html[\s\S]*?>', '<html>', source, flags=re.I)
        source = re.sub('</html>', '</html>', source, flags=re.I)
        # 格式化 head标签
        source = re.sub('<head[\s\S]*?>', '<head>', source, flags=re.I)
        source = re.sub('</head>', '</head>', source, flags=re.I)
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
        source = re.sub(r"<noscript>[\s\S]*?</noscript>", "", source, flags=re.I)
        # 匹配所有JS，过滤谷歌JS
        all_js = re.findall(r"<script[\s\S]*?>[\s\S]*?</script>", source, flags=re.I)
        for js_code in all_js:
            if any([i in js_code for i in ['google','elgoog','facebook','koobecaf','cnzz.com']]):
                source = source.replace(js_code, "")
        # 去回车
        source = "\n".join([i for i in source.strip().split('\n') if len(i.strip())>0])
        return source
    
    def index_repalce(self,source,conf):
        """首页替换处理"""
        title = conf["【首页TDK】"]['标题']
        des = conf["【首页TDK】"]['描述']
        keywords=conf["【首页TDK】"]['关键词']
        core_word = conf["【镜像配置】"]['核心词']
        replace_line = conf["【首页替换】"]["单行替换"]
        replace_lines = conf["【首页替换】"]["多行替换"]
        global_replace_line = conf["【全局替换】"]["单行替换"]
        global_replace_lines = conf["【全局替换】"]["多行替换"]
        # 核心词标签处理
        title = title.replace('{核心词}',core_word)
        des = des.replace('{核心词}',core_word)
        keywords = keywords.replace('{核心词}',core_word)
        replace_lines = replace_lines.replace('{核心词}',core_word)
        replace_line = [i.replace('{核心词}',core_word) for i in replace_line]
        global_replace_lines = global_replace_lines.replace('{核心词}',core_word)
        global_replace_line = [i.replace('{核心词}',core_word) for i in global_replace_line]
        # 过滤TDK
        if len(des)>1:
            # 转码处理
            if conf["【首页TDK】"]['转码'] and '{' not in des:
                des = self.func.transcoding(des)
            print(des)
            # 删除description
            source = re.sub(r'<meta.*?name="Description".*?/>', "", source, flags=re.I)
            source = re.sub(r"<meta.*?name='Description'.*?/>", "", source, flags=re.I)
            # 写入description
            source = source.replace('<head>',f'<head>\n<meta name="description" content="{des}" />')
        if len(keywords)>1:
            # 转码处理
            if conf["【首页TDK】"]['转码'] and '{' not in keywords:
                keywords = self.func.transcoding(keywords)
            # 删除keywords
            source = re.sub(r'<meta.*?name="Keywords".*?/>', "", source, flags=re.I)
            source = re.sub(r"<meta.*?name='Keywords'.*?/>", "", source, flags=re.I)
            # 写入keywords
            source = source.replace('<head>',f'<head>\n<meta name="keywords" content="{keywords}" />')
        if len(title)>1:
            # 转码处理
            if conf["【首页TDK】"]['转码'] and '{' not in title:
                title = self.func.transcoding(title)
            # 删除title
            source = re.sub(r"<title[\s\S]*?</title>", "", source, flags=re.I)
            # 写入title
            source = source.replace('<head>',f'<head>\n<title>{title}</title>')  
        # 单行替换
        for i in replace_line:
            if len(line:=i.split(" -> ",1))==2:
                try:
                    source = source.replace(line[0],line[1])
                except Exception as err:
                    print(i,str(err))
        # 多行替换
        for i in re.findall('r`([\s\S]*?)``([\s\S]*?)`',replace_lines):
            source = re.sub(i[0],i[1],source)
        for i in re.findall('r`[\s\S]*?``[\s\S]*?`',replace_lines):
            replace_lines = replace_lines.replace(i,'')
        for i in re.findall('`([\s\S]*?)``([\s\S]*?)`',replace_lines):
            source = source.replace(i[0],i[1])
        # 全局单行替换
        for i in global_replace_line:
            if len(line:=i.split(" -> ",1))==2:
                try:
                    source = source.replace(line[0],line[1])
                except Exception as err:
                    print(i,str(err))
        # 全局多行替换
        for i in re.findall('r`([\s\S]*?)``([\s\S]*?)`',global_replace_lines):
            source = re.sub(i[0],i[1],source)
        for i in re.findall('r`[\s\S]*?``[\s\S]*?`',global_replace_lines):
            global_replace_lines = global_replace_lines.replace(i,'')
        for i in re.findall('`([\s\S]*?)``([\s\S]*?)`',global_replace_lines):
            source = source.replace(i[0],i[1])
        return source

    def page_repalce(self,source,conf):
        """首页替换处理"""
        title = conf["【内页TDK】"]['标题']
        des = conf["【内页TDK】"]['描述']
        keywords=conf["【内页TDK】"]['关键词']
        core_word = conf["【镜像配置】"]['核心词']
        replace_line = conf["【内页替换】"]["单行替换"]
        replace_lines = conf["【内页替换】"]["多行替换"]
        global_replace_line = conf["【全局替换】"]["单行替换"]
        global_replace_lines = conf["【全局替换】"]["多行替换"]
        # 核心词标签处理
        title = title.replace('{核心词}',core_word)
        des = des.replace('{核心词}',core_word)
        keywords = keywords.replace('{核心词}',core_word)
        replace_lines = replace_lines.replace('{核心词}',core_word)
        replace_line = [i.replace('{核心词}',core_word) for i in replace_line]
        global_replace_lines = global_replace_lines.replace('{核心词}',core_word)
        global_replace_line = [i.replace('{核心词}',core_word) for i in global_replace_line]
        # 过滤TDK
        if len(des)>1:
            # 转码处理
            if conf["【首页TDK】"]['转码'] and '{' not in des:
                des = self.func.transcoding(des)
            print(des)
            # 删除description
            source = re.sub(r'<meta.*?name="Description".*?/>', "", source, flags=re.I)
            source = re.sub(r"<meta.*?name='Description'.*?/>", "", source, flags=re.I)
            # 写入description
            source = source.replace('<head>',f'<head>\n<meta name="description" content="{des}" />')
        if len(keywords)>1:
            # 转码处理
            if conf["【首页TDK】"]['转码'] and '{' not in keywords:
                keywords = self.func.transcoding(keywords)
            # 删除keywords
            source = re.sub(r'<meta.*?name="Keywords".*?/>', "", source, flags=re.I)
            source = re.sub(r"<meta.*?name='Keywords'.*?/>", "", source, flags=re.I)
            # 写入keywords
            source = source.replace('<head>',f'<head>\n<meta name="keywords" content="{keywords}" />')
        if len(title)>1:
            # 转码处理
            if conf["【首页TDK】"]['转码'] and '{' not in title:
                title = self.func.transcoding(title)
            # 删除title
            source = re.sub(r"<title[\s\S]*?</title>", "", source, flags=re.I)
            # 写入title
            source = source.replace('<head>',f'<head>\n<title>{title}</title>')  
        # 单行替换
        for i in replace_line:
            if len(line:=i.split(" -> ",1))==2:
                try:
                    source = source.replace(line[0],line[1])
                except Exception as err:
                    print(i,str(err))
        # 多行替换
        for i in re.findall('r`([\s\S]*?)``([\s\S]*?)`',replace_lines):
            source = re.sub(i[0],i[1],source)
        for i in re.findall('r`[\s\S]*?``[\s\S]*?`',replace_lines):
            replace_lines = replace_lines.replace(i,'')
        for i in re.findall('`([\s\S]*?)``([\s\S]*?)`',replace_lines):
            source = source.replace(i[0],i[1])
        # 全局单行替换
        for i in global_replace_line:
            if len(line:=i.split(" -> ",1))==2:
                try:
                    source = source.replace(line[0],line[1])
                except Exception as err:
                    print(i,str(err))
        # 全局多行替换
        for i in re.findall('r`([\s\S]*?)``([\s\S]*?)`',global_replace_lines):
            source = re.sub(i[0],i[1],source)
        for i in re.findall('r`[\s\S]*?``[\s\S]*?`',global_replace_lines):
            global_replace_lines = global_replace_lines.replace(i,'')
        for i in re.findall('`([\s\S]*?)``([\s\S]*?)`',global_replace_lines):
            source = source.replace(i[0],i[1])
        return source

    def replace(self,source,conf,is_index):
        """替换生成"""
        if is_index:
            source = self.index_repalce(source,conf)
        else:
            source = self.page_repalce(source,conf)
        return source