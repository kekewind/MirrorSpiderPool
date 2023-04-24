# -*- coding: UTF-8 -*-
"""标签解析器"""

import linecache
import os
import random
import re
import arrow
import tldextract
from func.function import Func
from func.const import *


class TagParser():
    """标签解析器"""

    def __init__(self, request,func):
        self.request = request
        self.func = func
        self.replace_data = []

    def custom(self, tag, tem):
        """自定义标签"""
        for k, value in tag['【自定义】'].items():
            tag_text = "{"+k+"}"
            if tag_text not in tem:
                continue
            if isinstance(value, str):
                tem = tem.replace(tag_text, value)
                self.replace_data.append((tag_text,value))
            else:
                for _ in re.findall(tag_text, tem):
                    value_ = random.choice(value)
                    tem = tem.replace(tag_text, value_, 1)
                    self.replace_data.append((tag_text,value_))
        return tem

    def extract_line(self, tag, tem):
        """文本抽取"""
        for k, file in tag['【文本抽取】'].items():
            tag_text = "{"+k+"}"
            if "{"+k not in tem:
                continue
            if isinstance(file, str):
                file_paths = []
                if os.path.isfile(file):
                    file_paths.append(file)
                else:
                    for f_name in os.listdir(file):
                        file_paths.append(os.path.join(file,f_name))
                for _ in re.findall(tag_text, tem):
                    file_path = random.choice(file_paths)
                    linecache.checkcache(file_path)
                    random_content = random.choice(linecache.getlines(file_path)).strip()
                    tem = tem.replace(tag_text, random_content, 1)
                    self.replace_data.append((tag_text,random_content))
                # 处理带ID
                t_texts = list(set(re.findall(tag_text[:-1]+"\d+}", tem)))
                for t_text in t_texts:
                    file_path = random.choice(file_paths)
                    linecache.checkcache(file_path)
                    random_content = random.choice(linecache.getlines(file_path)).strip()
                    tem = tem.replace(t_text, random_content)
                    self.replace_data.append((t_text,random_content))
            else:
                for _ in re.findall(tag_text, tem):
                    file_path = random.choice(file)
                    file_paths = []
                    if os.path.isfile(file_path):
                        file_paths.append(file_path)
                    else:
                        for f_name in os.listdir(file_path):
                            file_paths.append(os.path.join(file_path,f_name))
                    file_path = random.choice(file_paths)
                    linecache.checkcache(file_path)
                    random_content = random.choice(linecache.getlines(file_path)).strip()
                    tem = tem.replace(tag_text, random_content, 1)
                    self.replace_data.append((tag_text,random_content))
                # 处理带ID
                t_texts = list(set(re.findall(tag_text[:-1]+"\d+}", tem)))
                for t_text in t_texts:
                    file_path = random.choice(file)
                    file_paths = []
                    if os.path.isfile(file_path):
                        file_paths.append(file_path)
                    else:
                        for f_name in os.listdir(file_path):
                            file_paths.append(os.path.join(file_path,f_name))
                    file_path = random.choice(file_paths)
                    linecache.checkcache(file_path)
                    random_content = random.choice(linecache.getlines(file_path)).strip()
                    tem = tem.replace(t_text, random_content)
                    self.replace_data.append((t_text,random_content))
        return tem

    def extract_line0(self, tag, tem):
        """文本抽取 传参"""
        for k, file in tag['【文本抽取】'].items():
            re_tag_text = "{"+k+"\(.*?\)}"
            if "{"+k+"(" not in tem:
                continue
            if isinstance(file, str):
                file_paths = []
                if os.path.isfile(file):
                    file_paths.append(file)
                else:
                    for f_name in os.listdir(file):
                        file_paths.append(os.path.join(file,f_name))
                for _ in re.findall(re_tag_text, tem):
                    file_path = random.choice(file_paths)
                    linecache.checkcache(file_path)
                    random_content = random.choice(linecache.getlines(file_path)).strip()
                    text_ = re.findall(r"\((.*?)\)",_)[0]
                    if ',' in text_:
                        text,count = text_.split(',')
                        if '-' in count:
                            count_1,count_2 = count.split('-')
                            count = random.randint(int(count_1),int(count_2))
                    else:
                        text = text_
                        count = 1
                    # 关键词抽取
                    if "【关键词】" in random_content:
                        word = "【关键词】"
                        random_content = random_content.replace(word,text)
                    else:
                        keywords = self.func.get_text_keyword(random_content,k=int(count))
                        for word in keywords:
                            random_content = random_content.replace(word,text,1)
                    tem = tem.replace(_, random_content, 1)
                    self.replace_data.append((_,random_content))
            else:
                for _ in re.findall(re_tag_text, tem):
                    file_path = random.choice(file)
                    file_paths = []
                    if os.path.isfile(file_path):
                        file_paths.append(file_path)
                    else:
                        for f_name in os.listdir(file_path):
                            file_paths.append(os.path.join(file_path,f_name))
                    file_path = random.choice(file_paths)
                    linecache.checkcache(file_path)
                    random_content = random.choice(linecache.getlines(file_path)).strip()
                    text_ = re.findall(r"\((.*?)\)",_)[0]
                    if ',' in text_:
                        text,count = text_.split(',')
                        if '-' in count:
                            count_1,count_2 = count.split('-')
                            count = random.randint(int(count_1),int(count_2))
                    else:
                        text = text_
                        count = 1
                    # 关键词抽取
                    if "【关键词】" in random_content:
                        word = "【关键词】"
                        random_content = random_content.replace(word,text)
                    else:
                        keywords = self.func.get_text_keyword(random_content,k=int(count))
                        for word in keywords:
                            random_content = random_content.replace(word,text,1)
                    tem = tem.replace(_, random_content, 1)
                    self.replace_data.append((_,random_content))
        return tem


    def create_string(self, tag, tem):
        """字符生成"""
        for k, value in tag['【字符生成】'].items():
            # 处理单一 默认4-6字符
            tag_text = "{"+k+"}"
            custom_string = "{"+k[:2]+"4-6"+k[2:]+"}"
            if tag_text in tem:
                tem = tem.replace(tag_text, custom_string)
                self.replace_data.append((tag_text,custom_string))
            # 处理数量
            tag_head = k[:2]
            tag_foot = k[2:]
            count_tag = list(set(re.findall("{"+f'{tag_head}(\d+){tag_foot}'+"}", tem)))
            for count in count_tag:
                tag_text = "{"+tag_head+count+tag_foot+"}"
                while tag_text in tem:
                    content = "".join(random.choices(value, k=int(count)))
                    tem = tem.replace(tag_text, content, 1)
                    self.replace_data.append((tag_text,content))
            # 处理随机数量
            random_count_tag = list(set(re.findall("{"+f'{tag_head}(\d+)-(\d+){tag_foot}'+"}", tem)))
            for random_count in random_count_tag:
                tag_text = "{"+tag_head+"-".join(random_count)+tag_foot+"}"
                if int(random_count[0]) < int(random_count[1]):
                    while tag_text in tem:
                        count = random.randint(
                            int(random_count[0]), int(random_count[1]))
                        content = "".join(random.choices(value, k=int(count)))
                        tem = tem.replace(tag_text, content, 1)
                        self.replace_data.append((tag_text,content))
        return tem

    def get_info(self, tag, tem):
        """信息获取"""
        for i in tag['【信息获取】']:
            now = str(arrow.now('Asia/Shanghai'))
            tag_text = "{"+i+"}"
            if tag_text not in tem:
                continue
            if i == "年":
                text = str(arrow.now('Asia/Shanghai').year)
            elif i == "年月日":
                text = now.split('T')[0]
            elif i == "今日时间":
                text = now.split('.')[0].replace('T', ' ')
            elif i == "当前时间":
                text = now.split('.')[0].replace('T', ' ').split(' ')[-1]
            elif i == "当前域名":
                text = self.func.get_domain_info(str(self.request.base_url))[1]
            elif i == "当前主域名":
                text = self.func.get_domain_info(str(self.request.base_url))[-1]
            elif i == "当前url":
                text = str(self.request.url)
            tem = tem.replace(tag_text, text)
            self.replace_data.append((tag_text,text))
        return tem

    def extract_file_path(self, tag, tem):
        """文件抽取"""
        for k, file_dir in tag['【文件抽取】'].items():
            tag_text = "{"+k+"}"
            if tag_text not in tem:
                continue
            file_paths = [os.path.join(file_dir,name) for name in os.listdir(file_dir)]
            if len(file_paths) > 0:
                for _ in re.findall(tag_text, tem):
                    file_path = "/"+random.choice(file_paths)
                    tem = tem.replace(tag_text, file_path, 1)
                    self.replace_data.append((tag_text,file_path))
        return tem

    def html_coding(self,tem):
        """标签html实体转码"""
        need_trans_list = list(set(re.findall("{"+"(.*?)"+"}",tem)))
        for i in need_trans_list:
            if self.func.exists_chinese(i):
                code_word = self.func.transcoding(i)
                tem = tem.replace("{"+i+"}",code_word)
                self.replace_data.append(("{"+i+"}",code_word))
        return tem

    def get_title(self,tem):
        """获取标签title"""
        titles = re.findall('<title.*?>(.*?)</title>',tem,re.IGNORECASE)
        title = '' if len(titles)==0 else titles[0]
        return title
    
    def get_keyword(self,tem):
        """获取标签keywords"""
        keywords = re.findall('<meta name="keywords" content="(.*?)" />',tem,re.IGNORECASE)
        keywords = '' if len(keywords)==0 else keywords[0]
        keyword = keywords.split(',')[0]
        return keyword
        
    def parse(self, tem):
        """解析标签"""
        tag = self.func.get_yaml(TAG_PATH)
        # 自定义标签
        tem = self.custom(tag, tem)
        # 文本抽取 传参
        tem = self.extract_line0(tag, tem)
        # 文本抽取
        tem = self.extract_line(tag, tem)
        # 图片抽取
        tem = self.extract_file_path(tag, tem)
        # 字符生成
        tem = self.create_string(tag, tem)
        # 信息获取
        tem = self.get_info(tag, tem)
        # 处理{title}{keyword}
        title = self.get_title(tem)
        tem = tem.replace('{title}',title)
        keyword = self.get_keyword(tem)
        tem = tem.replace('{keyword}',keyword)
        # 处理HTML实体转码
        tem = self.html_coding(tem)
        return tem,self.replace_data