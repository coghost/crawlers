# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '2018/6/20 4:36 PM'
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

import house

# print = log.debug
wx_sess = requests.session()

wx_headers = {
    'Host': 'ztcwx.myscrm.cn',
    'Connection': 'keep-alive',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0; MIX 2 Build/OPR1.170623.027; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/6.2 TBS/044034 Mobile Safari/537.36 MicroMessenger/6.6.7.1320(0x26060734) NetType/WIFI Language/en',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,image/wxpic,image/sharpp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en,en-US;q=0.8',
}

api_url = {
    'verify_code': 'https://ztcwx.myscrm.cn/index.php?r=choose-room-activity/send-verify-code',
    'confirm_login': 'https://ztcwx.myscrm.cn/index.php?r=choose-room-activity/confirm-login',
}


def prepare():
    url, dat = house.parse_charles()
    cks = dat.pop('Cookie')
    url = 'https://ztcwx.myscrm.cn' + url
    print(url)
    cookies_ = house.fmt_cookies(cks)
    print(json.dumps(cookies_))
    return url, cookies_


def get_url_params(url):
    url_path, params = url.split('?')
    print(url_path, params)
    p = dict(parse_qsl(unquote_plus(params)))
    print(p)
    return


def get_login_page():
    # url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxa1a9602f479134ba&redirect_uri=https%3A%2F%2Fztcwx.myscrm.cn%2Findex.php%3Fr%3Dwx%2Findex%26yk_token%3Dfjsjpi1528359700%26go%3Dhttps%253A%252F%252Fztcwx.myscrm.cn%252Fpage%252Flogin.html%253FactivityId%253D3262%2526token%253Dfjsjpi1528359700%2526url%253Dhttps%25253A%25252F%25252Fztcwx.myscrm.cn%25252Fpage%25252Factivity.html%25253Ftoken%25253Dfjsjpi1528359700%252526activityId%25253D3262&response_type=code&scope=snsapi_base&state=1&connect_redirect=1#wechat_redirect'
    # url = 'https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxa1a9602f479134ba&redirect_uri=https%3A%2F%2Fztcwx.myscrm.cn%2Findex.php%3Fr%3Dwx%2Findex%26yk_token%3Dfjsjpi1528359700%26go%3Dhttps%253A%252F%252Fztcwx.myscrm.cn%252Fpage%252Flogin.html%253FactivityId%253D3262%2526token%253Dfjsjpi1528359700%2526url%253Dhttps%25253A%25252F%25252Fztcwx.myscrm.cn%25252Fpage%25252Factivity.html%25253Ftoken%25253Dfjsjpi1528359700%252526activityId%25253D3262&response_type=code&scope=snsapi_base&state=1&connect_redirect=1#wechat_redirect'
    # url = 'https://ztcwx.myscrm.cn/page/login.html?activityId=3262&token=fjsjpi1528359700&url=https%3A%2F%2Fztcwx.myscrm.cn%2Fpage%2Factivity.html%3Ftoken%3Dfjsjpi1528359700%26activityId%3D3262'
    # url = 'https://ztcwx.myscrm.cn/index.php?r=yunke/choose-room-activity-qr&activityId=3262&token=fjsjpi1528359700'
    url, cookies_ = prepare()
    print(url)
    get_url_params(url)
    return
    # return cookies_
    rs = wx_sess.get(url, verify=False, headers=wx_headers, cookies=cookies_)

    txt = BS(rs.content, 'html5lib', from_encoding='utf-8')
    print(txt)


def post_it():
    _, cookies_ = prepare()
    # url = 'https://ztcwx.myscrm.cn/index.php?r=choose-room-activity/send-verify-code'
    url = 'https://ztcwx.myscrm.cn/index.php?r=choose-room-activity'
    dat = {
        'activityId': '3261',
        'mobile': '18823171635',
        'token': 'fjsjpi1528359700',
    }
    rs = wx_sess.post(url, data=dat, cookies=cookies_)
    # print(rs.content)
    txt = BS(rs.content, 'html5lib', from_encoding='utf-8')
    print(txt)


def run():
    get_login_page()
    # post_it()


if __name__ == '__main__':
    run()
    # d = parse_charles()
    # post_cookies()