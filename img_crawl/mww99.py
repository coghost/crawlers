#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '23/12/2017 4:47 PM'
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
from urllib.parse import urljoin, urlencode
import re
from multiprocessing import Pool
import json

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from logzero import logger as log
from tqdm import tqdm
import click

from izen import helper
import base
from base.dbstore import rds, rdc

from base.crawl import Crawl
from base import abc
from base.abc import cfg

rdb_out = rdc(1)
# 初始化一个字典
mww_pages = rds.Dict(client=rdb_out, key='mww.pages')
mww_base = rds.Dict(client=rdb_out, key='mww.base')

M = {
    'index': 'http://m.99mww.com/gaoxiaotupian/',
    'page': 'http://m.99mww.com/gaoxiaotupian/l{}.html',
    'sub_page': 'http://m.99mww.com/{}',
    'baozou': 'http://m.99mww.com/baozoumanhua/159851.html',
    'xie': 'http://m.99mww.com/xieemanhua/159869.html',
}

enable_filter = False


class ImgDown(Crawl):
    def __init__(self, base_dir='/tmp/mww99'):
        Crawl.__init__(self, refer=M['index'], parser='html5lib', encoding='gbk')
        self.base_dir = base_dir
        self.store = {}

    def get_total_pages(self):
        log.debug('get pages')
        raw = self.bs4markup(self.do_get(M['index']))
        showpage = raw.find('div', 'showpage')
        for a in showpage.find_all('a'):
            if a.text == '末页':
                mww_total = int(a.get('href')[1:].split('.')[0])
                mww_base['total'] = mww_total

    def get_single_page(self, page_index=1):
        url = M['page'].format(page_index)
        raw = self.bs4markup(self.do_get(url))
        pic_raw = raw.find('div', 'c_inner')
        for li in pic_raw.find_all('li'):
            href = li.a.get('href')
            name = href.split('/')[-1].split('.')[0]
            mww_pages[name] = {
                'url': href,
                'name': name,
            }

    def get_all_page(self):
        for i in tqdm(range(int(mww_base.get('total'))), ascii=True):
            i += 1
            if i < int(mww_base.get('done', 0)):
                print('SKIP {}'.format(i))
                continue
            self.get_single_page(i)
            log.debug('DONE @ {}'.format(i))
            time.sleep(abc.randint(1, 4))
            mww_base['done'] = i

    def analy_xemh(self, page_num='159869'):
        url = 'http://m.99mww.com/xieemanhua/159869.html'
        raw = self.bs4markup(self.do_get(url))
        total = raw.find('div', 'lrcss').find_all('a')[0].text
        img = raw.find('div', id='imgString')
        print(img.img)

    def download_it(self):
        pass
        # url = 'http://dedeimg.minbean.com/uploads/allimg1/171218/0aapouwri2x.gif'
        # name = '0aabc.gif'
        # self.download_and_save({
        #     'img_url': url,
        #     'title': name,
        # })


@click.command()
@click.option('--index_page', '-i',
              type=int,
              help='the start index\nUSAGE: <cmd> -i <num>')
@click.option('--base_dir', '-d',
              help='the dir to store images\nUSAGE: <cmd> -d <dir_pth>')
@click.option('--update', '-u',
              is_flag=True,
              help='update total pages')
def run(index_page, base_dir, update):
    imd = ImgDown()
    # imd.download_it()
    imd.analy_xemh()
    # imd.get_all_page()
    if update or not mww_base.get('total'):
        imd.get_total_pages()
        abc.force_quit()
    if index_page:
        imd.get_single_page(index_page)


if __name__ == '__main__':
    run()
