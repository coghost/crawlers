# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '24/11/2017 12:46 PM'
__description__ = '''
1. the spider of [sdifen.com](www.sdifen.com)
'''

import os
import sys
import json
import requests

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import bs4
from logzero import logger as log
import click

from base.crawl import Crawl
from base import abc
from base.abc import cfg

from sdifen import selen

My = {
    'search': 'http://www.sdifen.com/?s={}&submit=搜索',
    'refer': 'https://sdifen.ctfile.com',
}


class Sdifen(Crawl):
    def __init__(self, refer=My.get('refer', ''), baidu_pwd_len=4, encoding='utf-8'):
        Crawl.__init__(self, refer, encoding=encoding)
        self.baidu_pwd_len = baidu_pwd_len

    def get_by_name(self, name=''):
        raw = self.bs4get(My.get('search').format(name))
        if not raw:
            sys.exit('cannot got {}'.format(name))

        art_docs = raw.find('div', id='content')
        candidates = self.get_articles(art_docs)
        if not candidates:
            sys.exit('cannot find {}'.format(name))

        i = abc.num_choice([
            '{} ({})'.format(c.get('txt'), c.get('netdisk'))
            for c in candidates])
        _soft_info = candidates[i]
        log.debug('Your Choice is: [{}]'.format(_soft_info['txt']))

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
            arts.append({
                'txt': txt,
                'url': url,
                'netdisk': _pan,
            })
        return arts

    def get_soft_pan(self, _url):
        rs = self.get_file_url({'url': _url})
        if not rs:
            return '官方下载'
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
def run(name):
    s = Sdifen()
    s.get_by_name(name)


if __name__ == '__main__':
    run()
