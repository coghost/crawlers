#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '11/16 22:17'
__description__ = '''
'''
import os
import sys
import time
import json
from urllib.parse import urljoin, urlencode, quote

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)
from izen.crawler import AsyncCrawler, UA
from bs4 import BeautifulSoup as BS
import wget

import requests
import click
from logzero import logger as log
from izen import helper

sess = requests.session()

json_header = {
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0',
    'Host': 'music.sonimei.cn',
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'http://music.sonimei.cn',
    'Content-Type': 'application/x-www-form-urlencoded',
}

Mli_api = 'https://music_api.dns.24mz.cn/index.php?'


class Mli(AsyncCrawler):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def fetch(self, name, author):
        songs = self.get_songs(name, author)
        if isinstance(songs, list):
            print(songs)
            return
        return self.get_song(songs['id'])

    def get_songs(self, name, author):
        params = {
            'types': 'search',
            'count': 5,
            'source': 'tencent',
            'pages': 1,
            'name': name,
            '_': helper.unixtime(True),
        }
        url_ = Mli_api + urlencode(params)
        print(url_)
        songs = self.bs4get(url_, is_json=True)
        songs = json.loads(songs)
        baks = []
        candidate = []
        for i, song in enumerate(songs):
            baks.append(song)
            b = author in song.get('artist', [])
            b = b and (name in song.get('name') or song.get('name') in name)
            if b:
                print(i, song)
                candidate.append(song)

        keys = ['demo', 'live']
        for k in keys:
            if len(candidate) == 1:
                return candidate[0]
            elif not candidate:
                return baks
            candidate = [x for x in candidate if k not in x]
        return candidate[0]

    def get_song(self, sid):
        params = {
            'types': 'url',
            'id': sid,
            'source': 'tencent',
            '_': helper.unixtime(True),
        }
        _url = Mli_api + urlencode(params)
        song = json.loads(self.bs4get(_url, is_json=True))
        return song


class YiTing(object):
    def __init__(self):
        self.url_ = 'http://music.sonimei.cn/'
        self.ac = AsyncCrawler(site_init_url=self.url_, overwrite=True, timeout=10)

    def search_it(self, name, author_=''):
        self.ac.headers['post'] = json_header
        form = {
            'filter': 'name',
            'type': 'qq',
            'page': 1,
            'input': name,
        }
        doc = self.ac.do_sess_post(self.url_, data=form, headers=json_header)
        songs = doc['data']
        if not songs:
            log.debug('no song found of {}/{}'.format(name, author_))
            os._exit(0)

        matched = []
        for i, song in enumerate(songs):
            matched.append({
                'title': '{}-{}'.format(song['author'], song['title']),
                'url': song['url']
            })
        return matched

    def get_best(self, songs, name, author_):
        _valid = []
        songs_bak = []
        for i, song in enumerate(songs):
            _title = '{}-{}'.format(song['author'], song['title'])
            url = song['url']
            songs_bak.append('{} {}'.format(_title, url))

            b = False or author_ in song['author'] or song['author'] in author_
            b = b and (name in song['title'] or song['title'] in name)
            if b:
                _valid.append('{} {}'.format(_title, url))

        keys = ['demo', 'live']
        for k in keys:
            if len(_valid) == 1:
                return _valid[0]
            elif not _valid:
                return songs_bak
            _valid = [x for x in _valid if k not in x]

        return _valid


def save_music(song):
    name = song['title']
    save_to = '/Users/lihe/Music/favor/' + name + '.mp3'
    if helper.is_file_ok(save_to):
        print('{} is existed.'.format(save_to))
        return
    print('try get {}'.format(save_to))
    wget.download(song['url'], out=save_to)
    print('downloaded {}'.format(save_to))

@click.command()
@click.option('--name', '-n',
              help='the name of song\nUSAGE: <cmd> -n <name>')
@click.option('--author', '-a',
              default='',
              help='the name of artist\nUSAGE: <cmd> -a <name>')
def run(name='', author=''):
    # pds('一路向北 - (电影《头文字D》插曲)')
    if not name:
        return
    if ',' in name:
        name, author = name.split(',')
    songs_ = YiTing().search_it(name, author)
    # songs_ = [' '.join(x.split(' ')[:-1]) for x in rs]
    titles = [x['title'] for x in songs_]
    n = helper.num_choice(titles)
    save_music(songs_[n])


if __name__ == '__main__':
    run()
    # m = Mli(site_init_url=Mli_api, overwrite=True)
    # song = m.fetch('认真地老去', '张希')
    # print(song)
