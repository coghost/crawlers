# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '27/10/2017 11:07 AM'
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

from base.crawl import Crawl
from base import abc
from base.abc import cfg

import requests

M = {
    'refer': 'http://www.cnplugins.com',
    'index': 'http://www.cnplugins.com/',
    'search': 'http://www.cnplugins.com/advsearch.php?q={}',
}


class Crx(Crawl):
    def __init__(self):
        Crawl.__init__(self, refer=M['refer'])

    def search(self, name='vue'):
        url = M['search'].format(name)
        raw = self.bs4markup(self.do_get(url))
        pages = []

        dls = raw.find('div', 'resultlist').find_all('dl')
        for dl in dls:
            rtitle = dl.find('dt', 'rtitle')
            pages.append({
                'name': rtitle.text,
                'url': '{}download.html'.format(rtitle.a.get('href')),
            })

        return pages

    def page_links(self, url=''):
        raw = self.bs4markup(self.do_get(url))
        desc = raw.find_all('span', 'info')
        name = ''
        for _ in desc:
            if _.text.find('插件名称') != -1:
                name = _.text.split('：')[1]
                break
        name = '_'.join(name.split(' '))

        down = raw.find('div', 'arc-down')
        for alk in down.find_all('a'):
            if alk.text.find('高速下载器下载二') != -1:
                return name, alk.get('href')


@click.command()
@click.option('--name', '-n',
              help='find by the name\nUSAGE: <cmd> -n <name>')
def run(name):
    crx = Crx()
    pages = crx.search(name)
    c = abc.num_choice([x['name'] for x in pages])
    page = pages[c]
    crx_name, url_pth = crx.page_links(page['url'])
    dat = url_pth.split('=')[1].split('&')[0]
    _url = 'http://down.cnplugins.com/down/down.aspx?fn={}'.format(dat)
    _wget_cmd = 'wget {} -O /tmp/{}.zip'.format(_url, crx_name)
    print('{}'.format(_wget_cmd))
    os.popen(_wget_cmd)


if __name__ == '__main__':
    run()
