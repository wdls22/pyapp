#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/1 下午1:17
# @Author  : Aries
# @Site    : 
# @File    : Utinity.py
# @Software: PyCharm

import urllib


def convert_url_uni(arg):
    arg = urllib.unquote(arg.encode('utf-8')).decode('utf-8')
    return arg
