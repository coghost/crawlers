#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '01/12/2017 4:22 PM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''

import os
import sys

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from urllib.parse import urljoin, urlencode
import time

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import click
from izen import helper

from base.crawl import Crawl
from base import abc
from base.abc import cfg
import requests
import json

M = {
    'refer': 'https://www.taobao.com',
    'index': 'https://www.taobao.com/',
    'search': 'https://login.taobao.com/',
}


class Tb(Crawl):
    def __init__(self):
        Crawl.__init__(self, refer=M['refer'])
        self.sess = requests.session()

    def login(self):
        headers = {
            'Host': 'login.taobao.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://login.taobao.com/',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        form = {
            'TPL_username': cfg.get('taobao.username'),
            'TPL_password_2': cfg.get('taobao.password'),
            'ua': cfg.get('taobao.ua'),
            'TPL_password': '',
            'ncoSig': '',
            'ncoSessionid': '',
            'ncoToken': '5aef16011b56475a4e16804cd8f849c07411ce6e',
            'slideCodeShow': 'false',
            'useMobile': 'false',
            'lang': 'zh_CN',
            'loginsite': '0',
            'newlogin': '0',
            'TPL_redirect_url': 'https://i.taobao.com/my_taobao.htm',
            'from': 'tb',
            'fc': 'default',
            'style': 'default',
            'css_style': '',
            'keyLogin': 'false',
            'qrLogin': 'true',
            'newMini': 'false',
            'newMini2': 'false',
            'tid': '',
            'loginType': '3',
            'minititle': '',
            'minipara': '',
            'pstrong': '',
            'sign': '',
            'need_sign': '',
            'isIgnore': '',
            'full_redirect': '',
            'sub_jump': '',
            'popid': '',
            'callback': '',
            'guf': '',
            'not_duplite_str': '',
            'need_user_id': '',
            'poy': '',
            'gvfdcname': '10',
            'gvfdcre': '68747470733A2F2F6C6F67696E2E74616F62616F2E636F6D2F6D656D6265722F6C6F676F75742E6A68746D6C3F73706D3D61317A30322E312E3735343839343433372E372E313565366266393469465247474D26663D746F70266F75743D7472756526726564697265637455524C3D6874747073253341253246253246692E74616F62616F2E636F6D2532466D795F74616F62616F2E68746D2533466E656B6F742533445932396E6147397A64412532353344253235334431353132313137333731393837',
            'from_encoding': '',
            'sub': '',
            'loginASR': '1',
            'loginASRSuc': '1',
            'allp': '',
            'oslanguage': 'zh-CN',
            'sr': '1280*800',
            'osVer': 'macos%7C10.13',
            'naviVer': 'firefox%7C57',
            'osACN': 'Mozilla',
            'osAV': '5.0+%28Macintosh%29',
            'osPF': 'MacIntel',
            'miserHardInfo': '',
            'appkey': '',
            'nickLoginLink': '',
            'mobileLoginLink': 'https://login.taobao.com/member/login.jhtml?redirectURL=https://i.taobao.com/my_taobao.htm?nekot=Y29naG9zdA%3D%3D1512117371987&useMobile=true',
            'showAssistantLink': '',
            'um_token': 'HV01PAAZ0baf4049de800f3f5a21149b0068cb7a',
        }
        dat = {
            'url': 'https://login.taobao.com/member/login.jhtml?redirectURL=https://i.taobao.com/my_taobao.htm?nekot=Y29naG9zdA%3D%3D1512117371987',
            'headers': headers,
            # 'data': 'TPL_username=coghost&TPL_password=&ncoSig=&ncoSessionid=&ncoToken=5aef16011b56475a4e16804cd8f849c07411ce6e&slideCodeShow=false&useMobile=false&lang=zh_CN&loginsite=0&newlogin=0&TPL_redirect_url=https%3A%2F%2Fi.taobao.com%2Fmy_taobao.htm%3Fnekot%3DY29naG9zdA%253D%253D1512117371987&from=tb&fc=default&style=default&css_style=&keyLogin=false&qrLogin=true&newMini=false&newMini2=false&tid=&loginType=3&minititle=&minipara=&pstrong=&sign=&need_sign=&isIgnore=&full_redirect=&sub_jump=&popid=&callback=&guf=&not_duplite_str=&need_user_id=&poy=&gvfdcname=10&gvfdcre=68747470733A2F2F6C6F67696E2E74616F62616F2E636F6D2F6D656D6265722F6C6F676F75742E6A68746D6C3F73706D3D61317A30322E312E3735343839343433372E372E313565366266393469465247474D26663D746F70266F75743D7472756526726564697265637455524C3D6874747073253341253246253246692E74616F62616F2E636F6D2532466D795F74616F62616F2E68746D2533466E656B6F742533445932396E6147397A64412532353344253235334431353132313137333731393837&from_encoding=&sub=&TPL_password_2=539e25a6d4b54376c4d75ba10adc8ac7e745010d02e4e34f80abd336d6d07effdd11d0f2ed1993e6b955855a2c90531280b55c6218a67e94deca86dd5d45563833b30853c2b3bb70d160c158a327e487bd95c5b14bf7530f63011660f651a94853886e966ecdecf81dbe86adcc793eeff584453e36b948500fb16b5c5309ec40&loginASR=1&loginASRSuc=1&allp=&oslanguage=zh-CN&sr=1280*800&osVer=macos%7C10.13&naviVer=firefox%7C57&osACN=Mozilla&osAV=5.0+%28Macintosh%29&osPF=MacIntel&miserHardInfo=&appkey=&nickLoginLink=&mobileLoginLink=https%3A%2F%2Flogin.taobao.com%2Fmember%2Flogin.jhtml%3FredirectURL%3Dhttps%3A%2F%2Fi.taobao.com%2Fmy_taobao.htm%3Fnekot%3DY29naG9zdA%253D%253D1512117371987%26useMobile%3Dtrue&showAssistantLink=&um_token=HV01PAAZ0baf4049de800f3f5a21149b0068cb7a'
        }
        self.sess.post(
            dat['url'],
            data=urlencode(form),
            headers=headers,
        )
        # print(res.text)
        # raw = self.bs4markup(
        #     self.sess.get('https://i.taobao.com/my_taobao.htm?nekot=Y29naG9zdA==1512117371987').content)
        # print(raw.head)
        # s.get('https://login.taobao.com/member/logout.jhtml?f=top&out=true')

        # print('\n' * 10)
        # raw = self.bs4markup(self.sess.get('https://i.taobao.com/my_taobao.htm?nekot=Y29naG9zdA==1512117371987').content)
        # print(raw.head)

        # raw = self.bs4markup(self.do_post(dat))
        # print(raw)

    def bought_items(self):
        url = 'https://buyertrade.taobao.com/trade/itemlist/list_bought_items.htm'
        raw = self.bs4markup(
            self.sess.get(url).content)
        print(raw)
        _jbm = raw.find('div', id='J_bought_main')
        # print(_jbm)
        print('\n')
        bought = raw.find_all('div', 'index-mod__order-container___1ur4- js-order-container')
        print(len(bought))

    def logout(self):
        self.sess.get('https://login.taobao.com/member/logout.jhtml?f=top&out=true')

    def load(self):
        dat = json.loads(helper.to_str(helper.read_file('items.json')))
        return dat


def run():
    tb = Tb()
    # tb.login()
    # tb.bought_items()
    # tb.logout()
    dat = tb.load()
    print(json.dumps(dat, indent=2))


if __name__ == '__main__':
    run()
