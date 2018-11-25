# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '11/25 12:14'
__description__ = '''
- [墨灵音乐](https://music.mli.im/)
'''

import os
import sys
import json
from urllib.parse import urljoin, urlencode, quote

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

from izen import helper
from izen.crawler import AsyncCrawler, UA

Mli_home = 'https://music_api.dns.24mz.cn/index.php?'


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
        url_ = Mli_home + urlencode(params)
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
        _url = Mli_home + urlencode(params)
        song = json.loads(self.bs4get(_url, is_json=True))
        return song


if __name__ == '__main__':
    pass
