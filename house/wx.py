# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '2018/6/20 2:30 PM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''

import os
import sys

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

import requests
from bs4 import BeautifulSoup as BS
from izen import helper
from urllib.parse import urljoin, urlencode, quote, unquote_plus, parse_qsl
from logzero import logger as log

wx_sess = requests.session()

urls = {
    'wx': 'https://wx.qq.com'
}


def _wx():
    res = wx_sess.get(urls['wx'])
    print(res.content)


def run():
    _wx()


if __name__ == '__main__':
    run()
