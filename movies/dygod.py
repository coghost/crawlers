#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '27/11/2017 6:22 PM'
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

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from logzero import logger as log
import click

from izen import helper

from base.crawl import Crawl
from base import abc

My = {
    'home': 'http://www.ygdy8.com/',
    'refer': 'http://s.dydytt.net/plus/so.php',
    'search': 'http://s.dydytt.net/plus/search.php?',
}


class Dygod(Crawl):
    def __init__(self,
                 refer=My.get('refer', ''),
                 encoding='gb2312',
                 parser='html5lib',
                 ):
        Crawl.__init__(self, refer,
                       encoding=encoding,
                       parser=parser)

    def search(self, name=''):
        params = urlencode({
            'kwtype': 0,
            'keyword': name.encode('gbk')
        })
        url = '{}{}'.format(My['search'], params)
        movies = []
        while url:
            raw = self.bs4markup(self.stream_get({'url': url}))
            if not raw:
                continue
            tables = raw.find('div', 'co_content8')
            url = self.has_page_next(tables)
            _mvs = tables.find_all('a')
            for mv in _mvs:
                movies.append({
                    'name': mv.text,
                    'url': urljoin(My['home'], mv.get('href'))
                })

        movies = [x for x in movies if x['name'].find(name) != -1]
        return movies

    @staticmethod
    def has_page_next(docs):
        so = docs.find_all('a')
        for alk in so:
            if alk.text.find('下一页') != -1:
                return urljoin(My['search'], alk.get('href'))

    def page_links(self, name='', page_url=''):
        movies = []
        raw = self.bs4markup(self.do_get({'url': page_url}))
        if not raw:
            return movies

        zoom = raw.find('div', id='Zoom')
        tables = zoom.find_all('table')

        for table in tables:
            links = table.find_all('a')
            for lk in links:
                movies.append({
                    'url': lk.get('href'),
                    'name': lk.text,
                })

        movies = [x for x in movies if x['name'].find(name) != -1]
        return movies


@click.command()
@click.option('--name', '-n',
              help='find by the name\nUSAGE: <cmd> -n <name>')
def run(name):
    dy = Dygod()
    movie_pages = dy.search(name)
    choice_list = []

    _cis = [x['name'] for x in movie_pages]
    choice_list.append(_cis)

    while choice_list:
        c = helper.num_choice(choice_list[-1])
        if str(c) in 'bB' and len(choice_list) == 1:
            continue

        page_url = movie_pages[c].get('url')
        movies = dy.page_links(name, page_url)
        if not movies:
            log.warn('\nnothing got from ({})\n'.format(page_url))
            continue

        choice_list.append([x['name'] for x in movies])
        c = helper.num_choice(choice_list[-1], depth=2)
        choice_list.pop()

        if str(c) in 'bB':
            continue

        link = movies[c].get('url')

        log.debug('\n{}\ndownload link url has been copied to [clipboard]!\n'.format(link))
        helper.copy_to_clipboard(link)
        return


if __name__ == '__main__':
    run()
