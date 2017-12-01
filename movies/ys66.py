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
import json
import time
from urllib.parse import urljoin, urlencode

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from logzero import logger as log
import click
from tqdm import tqdm

from base.crawl import Crawl
from base import crawl
from base import abc
from base import selen
from base.abc import cfg

My = {
    'refer': 'http://www.dygang.net/sous.html',
    'search': 'http://so.dygang.net/e/search/index.php',
}


class Ys66(Crawl):
    def __init__(self,
                 refer=My.get('refer', ''),
                 encoding='gb2312',
                 parser='html5lib',
                 blur_match=True,
                 ):
        Crawl.__init__(self, refer, encoding=encoding, parser=parser)
        self.blur_match = blur_match
        self.search_type = {
            1: 'title',
            3: 'smalltext',
            5: 'title,smalltext',
        }

    def page_links(self, name='', url=''):
        raw = self.bs4markup(self.do_get({'url': url}))
        # raw = self.bs4markup(self.crawl(url))
        dede = raw.find('td', id='dede_content')
        tables = dede.find_all('table')

        if self.blur_match and not tables:
            return

        p_movies = dede.find_all('p')
        movies = []
        for table in tables:
            for tr in table.find_all('tr'):
                try:
                    if self.blur_match and not tr.td.text:
                        return movies
                    if not tr.td.find('a'):
                        continue
                    movies.append({
                        'name': tr.td.text,
                        'url': tr.td.a.get('href')
                    })
                except AttributeError as _:
                    pass
                    log.debug('error {} of {}'.format(_, tr))

        if not self.blur_match:
            for pm in p_movies:
                al = pm.find('a')
                if not al:
                    continue
                movies.append({
                    'name': al.text,
                    'url': al.get('href')
                })

        movies = [x for x in movies
                  if x['name'].find('\n') == -1 and x['name'].find(name) != -1]

        return movies

    def search(self, name='', area=5):
        movies = []
        url = self.name2url(name, area)

        while url:
            raw = self.bs4markup(self.stream_get({'url': url}))
            # raw = self.bs4get(url)
            url = self.has_page_next(raw)
            _mvs = raw.find_all('a', 'classlinkclass')
            for mv in _mvs:
                movies.append({
                    'name': mv.text,
                    'url': mv.get('href')
                })

        return movies

    @staticmethod
    def has_page_next(docs):
        so = docs.find_all('a')
        for alk in so:
            if alk.text.find('下一页') != -1:
                return urljoin(My['search'], alk.get('href'))

    def name2url(self, name='', area=5):
        search_dat = urlencode({
            'tempid': 1,
            'tbname': 'article',
            'keyboard': name.encode('gbk'),
            'show': self.search_type[area],
            'Submit': '搜索'.encode('gbk'),
        })
        dat = {
            'url': My['search'],
            'data': search_dat,
            'allow_redirects': False,
        }
        # _url_map = self.do_post(dat, use_redirect_location=True)
        _url_map = self.stream_post(dat, use_redirect_location=True, show_bar=True)
        _url_map = urljoin(My['search'], _url_map)
        return _url_map


@click.command()
@click.option('--name', '-n',
              help='find by the name\nUSAGE: <cmd> -n <name>')
@click.option('--blur_match', '-b',
              is_flag=True,
              help='use blue match mode\nUSAGE: <cmd> -b')
@click.option('--area', '-a',
              default=5,
              help='search area in[1,3,5] default 5\nUSAGE: <cmd> -a <num>')
def run(name, area, blur_match):
    y = Ys66(blur_match=not blur_match)
    movie_pages = y.search(name, area)

    choice_list = []
    _cis = [x['name'] for x in movie_pages]
    choice_list.append(_cis)

    while choice_list:
        c = abc.num_choice(choice_list[-1])
        if str(c) in 'bB' and len(choice_list) == 1:
            continue

        movies = y.page_links(name, movie_pages[c].get('url'))
        if not movies:
            log.warn('\nnothing got from ({})\n'.format(movie_pages[c].get('url')))
            continue

        choice_list.append([x['name'] for x in movies])
        c = abc.num_choice(choice_list[-1], depth=2)
        choice_list.pop()

        if str(c) in 'bB':
            continue

        link = movies[c].get('url')

        if link.find('pan.baidu.com') != -1:
            pwd = movies[c].get('name').replace(' ', '').split('：')[-1]
            selen.baidu_pan_by_chrome(link, pwd)
        else:
            log.debug('\n{}\ndownload link url has been copied to [clipboard]!\n'.format(link))
            abc.set_clipboard_data(link)
        return


if __name__ == '__main__':
    # dat = tes()
    # print(dat)
    # os._exit(-1)
    # print(dat.find('title'))
    run()
