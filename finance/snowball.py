#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '2018/8/13 17:12'
__description__ = '''
'''
import json
import os
import sys
import time
from multiprocessing import Pool, cpu_count

import bs4
import click
from bs4 import BeautifulSoup as BS
from izen import helper
from logzero import logger as log
from tqdm import tqdm

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

from base import abc, crawl
from base.crawl import Crawl

SNOW = 'https://xueqiu.com'
s_pth = os.path.basename(__file__).split('.')[0]

M = {
    'save_to': os.path.expanduser('~/tmp/.{}'.format(s_pth)),
    'auto': SNOW + '{}',
    'detail': SNOW + '{}',
    'test': 'https://xueqiu.com/5476032336/112054274',
    'index': SNOW,
}


class Snowball(Crawl):
    """Snowball"""

    def __init__(self, parser='lxml'):
        super().__init__(parser=parser)
        self.parser = parser
        self.url = ''

    def crawl_page(self, _url, f):
        hot = self.bs4get(_url)
        helper.write_file(hot, f)

    def load_raw(self, _url, name=''):
        self.url = _url
        if not name:
            name = _url.split('/')[-1]
        f = os.path.join(M['save_to'], 'html/{}'.format(name))
        if not helper.is_file_ok(f):
            self.crawl_page(_url, f)
        doc = helper.read_file(f)
        doc = crawl.BS(doc, self.parser)
        return doc


class SnowProcess(object):
    """Snow doc Process"""

    def __init__(self, doc):
        self.doc = doc
        # self.parse_content()

    def parse_content(self):
        dat = self.doc.find('div', class_='article__bd__detail')
        print(dat.text)


def run():
    sb = Snowball()
    dat = sb.load_raw(M['test'])
    sp = SnowProcess(dat)
    sp.parse_content()


if __name__ == '__main__':
    run()
