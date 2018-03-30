#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '06/11/2017 4:01 PM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''

import os
import sys
from urllib.parse import urljoin, urlencode
import time

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from logzero import logger as log
from tqdm import tqdm
import click
import json
from multiprocessing import Pool
from izen import helper

from base.crawl import Crawl
from base import abc
from base.abc import cfg

import requests

host = 'http://m.wufazhuce.com/'
M = {
    'index': urljoin(host, 'index/'),
    'one': urljoin(host, 'one/'),
    'article': urljoin(host, 'article/'),
    'music': urljoin(host, 'music/'),
    'movie': urljoin(host, 'movie/'),
    'ajaxlist': 'http://m.wufazhuce.com/one/ajaxlist/',
}


class One(Crawl):
    def __init__(self, base_dir='/tmp/one'):
        Crawl.__init__(self, refer=M['index'])
        self.base_dir = base_dir
        self.current_id = 0
        self.sess = requests.session()

    def load_cache(self):
        self.ones = json.loads(helper.read_file('one.1910.all.json'))

    def fetch_one(self, depth=1):
        r = self.bs4markup(self.sess.get(M['one']).text)

        script_raw = r.find('div', role='main').find('script')
        if not script_raw:
            return

        token = ''
        for line in script_raw.text.split('\n'):
            if line.find('token') != -1:
                token = line.split('\'')[1]
                break
        log.debug('ajaxlist token: {}'.format(token))

        all_data = []

        while depth:
            ajax_url = '{}{}?_token={}'.format(M['ajaxlist'], self.current_id, token)
            log.debug('fetch {}'.format(ajax_url))
            cnt = self.sess.get(ajax_url)
            dat = cnt.json()
            all_data += dat['data']
            self.current_id = all_data[-1]['id']
            time.sleep(1)
            depth -= 1

            if len(dat['data']) < 10:
                break

        helper.write_file(json.dumps(all_data), 'one.all.json')
        return all_data


@click.command()
@click.option('--page_num', '-p',
              default=1,
              help='how many page will fetch\nUSAGE: <cmd> -p <num>')
def run(page_num):
    one = One()
    # one.load_cache()
    # print(len(one.ones))
    cnts = one.fetch_one(page_num)
    for cnt in cnts:
        print(json.dumps(cnt, indent=2))


if __name__ == '__main__':
    run()
