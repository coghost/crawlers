# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '11/25 21:02'
__description__ = '''
'''

import os
import sys
from dataclasses import dataclass

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

from izen.crawler import UA, ParseHeaderFromFile

__post_header__ = {
    'User-Agent': UA.mac_safari__,
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Content-Type': 'application/x-www-form-urlencoded',
}


class Headers:
    get: dict = {}
    post: dict = {}


class SonimeiHeaders(Headers):
    get: dict = {}
    post: dict = dict({
        'Host': 'music.sonimei.cn',
        'Referer': 'http://music.sonimei.cn',
    }, **__post_header__)


class NeteaseHeaders(Headers):
    get: dict = ParseHeaderFromFile('netease.txt').headers
    post: dict = ParseHeaderFromFile('netease_post.txt').headers
