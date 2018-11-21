#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '24/11/2017 12:46 PM'
__description__ = '''
1. the spider of [sdifen.com](www.sdifen.com)
'''

import os
import sys
import time
from dataclasses import dataclass

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)

from logzero import logger as log
import click
from izen import helper, crawler
from base import abc, selen


@dataclass
class M:
    index: str = 'https://sdifen.ctfile.com'
    search: str = 'http://www.sdifen.com/page/{}/?s={}&submit=搜索'
    refer: str = 'https://sdifen.ctfile.com'


class Sdifen(crawler.CommonCrawler):
    def __init__(self, baidu_pwd_len=4, parser='lxml', encoding='utf-8', **kwargs):
        self.bs = {
            'parser': parser,
            'encoding': encoding,
        }
        super().__init__(**kwargs)
        self.baidu_pwd_len = baidu_pwd_len
        self.netdisk = kwargs.get('netdisk', False)

    def get_by_name(self, name='', page_num=1):
        log.debug('get {} with page {}'.format(name, page_num))
        _ts = time.time()
        raw = self.bs4get(M.search.format(page_num, name))
        _te = time.time()
        if _te - _ts > 5:
            log.warning('Take {}s to fetch!'.format(_te - _ts))

        if not raw:
            sys.exit('cannot got {}'.format(name))

        art_docs = raw.find('div', id='content')
        has_next_page = raw.find_all('a', class_='nextpostslink')
        candidates, total = self.get_articles(art_docs)
        if not candidates:
            log.warning('valid/total {}/{}, try without `-d`'.format(name, total))
            return

        softs = ['{} ({})'.format(c.get('txt'), c.get('netdisk'))
                 for c in candidates]

        while True:
            c = helper.num_choice(
                softs,
                default=1,
                valid_keys='n,N,p,P'
            )
            if not c:
                return c

            if str(c) in 'bB':
                return

            if str(c) in 'nN':
                if has_next_page:
                    page_num += 1
                    return self.get_by_name(name, page_num)
                else:
                    log.warning('page {} is last page, check previous page with <pP> instead'.format(page_num))
                    continue

            if str(c) in 'pP':
                page_num -= 1
                return self.get_by_name(name, page_num)

            if c:
                c = int(c) - 1
                _soft_info = candidates[c]
                log.debug('Your Choice is: [{}]'.format(_soft_info['txt']))
                self.do_download(_soft_info)

    def do_download(self, _soft_info):
        soft = self.get_file_url(_soft_info)
        if not soft:
            log.error('cannot get file: ({})'.format(_soft_info['txt']))
            return
        else:
            log.debug('Try: [{}]({})'.format(_soft_info['txt'], soft[1]))

        if soft[0] == 1:
            selen.ctfile_by_chrome(soft[1])
        elif soft[0] == 3:
            selen.baidu_pan_by_chrome(soft[1], soft[2])
        else:
            log.warn('Not Support')

    def get_articles(self, docs):
        _no_art = docs.find('h1', 'entry-title')
        if _no_art.text.find('未找到') != -1:
            return None

        arts_raw = docs.find_all('article')
        arts = []
        for i, art in enumerate(arts_raw, start=1):
            txt = art.header.h1.a.text
            url = art.header.h1.a.get('href')
            _pan = self.get_soft_pan(url)
            if self.netdisk:
                if _pan:
                    arts.append({
                        'txt': txt,
                        'url': url,
                        'netdisk': _pan,
                    })
            else:
                arts.append({
                    'txt': txt,
                    'url': url,
                    'netdisk': _pan or 'x' * 3,
                })
        return arts, len(arts_raw)

    def get_soft_pan(self, _url):
        rs = self.get_file_url({'url': _url})
        if not rs:
            return ''
        return '百度网盘' if rs[0] == 3 else '城通网盘'

    def get_file_url(self, candi):
        raw = self.bs4get(candi.get('url', ''))
        if not raw:
            sys.exit('cannot got {}'.format(candi))

        entry = raw.find('div', 'entry-content')

        def get_pan(_url):
            if _url.find('ctfile.com') != -1:
                return 1, _url
            if _url.find('baidu.com') != -1:
                return 3, _url

        for p in entry.find_all('p'):
            if p.find('a'):
                pan = get_pan(p.a.get('href'))
                if not pan:
                    continue

                if pan[0] == 3:
                    pwd = p.text.replace(' ', '')[-self.baidu_pwd_len:]
                    return pan[0], pan[1], pwd
                return pan


@click.command()
@click.option('--name', '-n',
              help='the name of software\nUSAGE: <cmd> -n <name>')
@click.option('--netdisk', '-d',
              is_flag=True,
              help='the name should has a valid net disk link\nUSAGE: <cmd> -d')
def run(name, netdisk):
    log.debug('{} => {}'.format(name, netdisk))
    s = Sdifen(site_init_url=M.index, netdisk=netdisk, log_level=20)
    s.get_by_name(name)


if __name__ == '__main__':
    run()
