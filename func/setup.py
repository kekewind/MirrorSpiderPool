# -*- coding: UTF-8 -*-

from distutils.core import setup
from Cython.Build import cythonize
import os
import shutil

#[]内是要打包的文件名，也可多个文件
files = []
for file in os.listdir("./"):
    if file[-3:] == ".py" and file!="setup.py":
        files.append(file)
setup(ext_modules = cythonize(files))

# 删除 .c文件
for file in os.listdir("./"):
    if file[-2:] == ".c":
        os.remove(file)

for root, dirs, files in os.walk("./"):
    if "lib.linux" in root:
        for file in files:
            f_name_list = file.split(".")
            f_name = ".".join([f_name_list[0],f_name_list[-1]])
            shutil.move(f"{root}/{file}", f'./{f_name}')
# 删除 build
shutil.rmtree("./build")