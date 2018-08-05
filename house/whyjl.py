# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '2018/6/20 5:01 PM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''

import os
import sys
import json

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

import requests
from bs4 import BeautifulSoup as BS
from izen import helper
from urllib.parse import urljoin, urlencode, quote, unquote_plus, parse_qsl
from logzero import logger as log

from house import myyk

wx_sess = requests.session()
mh = myyk.MkHeader('whyjl.txt')
requests.packages.urllib3.disable_warnings()


def get_login_page():
    print('SESS:{}'.format(mh.cookies.get('PHPSESSID')))
    rs = wx_sess.get(mh.url, verify=False, headers=mh.headers, cookies=mh.cookies)

    txt = BS(rs.content, 'html5lib', from_encoding='utf-8')
    print(txt)


def run():
    print(mh.url)
    get_login_page()
    # post_it()


if __name__ == '__main__':
    run()
    # d = parse_charles()
    # post_cookies()
