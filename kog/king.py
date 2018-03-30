# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '17/12/2017 5:03 PM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''
import os
import sys
import time
import json
from urllib.request import unquote
import binascii

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

import rsa
import wget

from logzero import logger as log
import click
from tqdm import tqdm
from izen import helper
from base.crawl import Crawl

from base import abc
from base import dbstore
from base.abc import cfg

import requests

# 从文件读取headers信息从处理
Headers = {}
with open('headers.log', 'r') as df:
    for kv in [d.strip().split(':') for d in df]:
        Headers[kv[0]] = kv[1]

M = {
    'refer': 'http://pvp.qq.com',
    'hisrecord': 'http://pvp.qq.com/web201605/hisrecord.shtml'
}


class King(Crawl):
    def __init__(self,
                 refer=M.get('refer', ''),
                 ):
        Crawl.__init__(self, refer)

    def get_person_info(self):
        url = 'http://apps.game.qq.com/ams/ame/getWXUser.php?access_token=4_6D7rUdhhKdId3nmesaB4nROSp9a1YUGsFU5yIHleZXxnYC7cj6xjXm1_jFN2kDjMMq9HRk31w8J9wVnBIcfNBA&openid=owanlslpyPtjCQF9HMxLMsSeY2Gw&_=1513501589070'
        raw = requests.get(url)
        print(raw)
        print(raw.content)

    def get_history(self):
        params = {
            # 'url': M['hisrecord'],
            'headers': Headers,
        }
        raw = self.bs4markup(self.do_get(params))
        print(raw)


# 获取原始内容
# r = requests.get(url, headers=Headers)

def run():
    king = King()
    king.get_person_info()
    # king.get_history()


if __name__ == '__main__':
    run()
