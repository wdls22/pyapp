#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/2 下午10:23
# @Author  : Aries
# @Site    : 
# @File    : zhihu.py
# @Software: PyCharm

import requests
import os
from urlparse import urlsplit
from os.path import basename
import re
import urllib2


def get_image_url(qid):
    # use reg to get pic url
    # reg = r'data-actualsrc="(.*?)">'
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
        'Accept-Encoding': 'gzip, deflate'}
    tmp_url = "https://www.zhihu.com/node/QuestionAnswerListV2"
    size = 10
    image_urls = []
    session = requests.Session()
    while True:
        print '*****************************'
        post_data = {'method': 'next', 'params': '{"url_token":' +
                                                str(qid) + ',"pagesize": "10",' + '"offset":' + str(size) + "}"}

        page = session.post(tmp_url, headers=headers, data=post_data)
        ret = eval(page.text)
        answers = ret['msg']
        print u"答案数 : %d " % (len(answers))
        size += 10
        if not answers:
            print "图片URL获取完毕, 页数: ", (size - 10) / 10
            return image_urls
            # reg = r'https://pic\d.zhimg.com/[a-fA-F0-9]{5,32}_\w+.jpg'
        imgreg = re.compile('data-original="(.*?)"', re.S)
        for answer in answers:
            tmp_list = []
            url_items = re.findall(imgreg, answer)
            for item in url_items:  # delete '\\' in  pic url
                image_url = item.replace("\\", "")
                tmp_list.append(image_url)
                # clean get data-original
            tmp_list = list(set(tmp_list))  # distinct
            for item in tmp_list:
                if item.endswith('r.jpg'):
                    print item
                    image_urls.append(item)
        print 'size: %d, num : %d' % (size, len(image_urls))
