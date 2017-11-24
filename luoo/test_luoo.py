# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '07/11/2017 4:10 PM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''

import os
import sys
import unittest

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from bs4 import BeautifulSoup as BS
from luoo import app


class BaseTest(unittest.TestCase):
    @unittest.skip
    def test_luoo_music(self):
        lm = app.LuooMusic()
        lm.init()
        self.assertIsNotNone(lm.page_count)
        self.assertIsNotNone(lm.category)
        self.assertIsInstance(lm.page_count, int)
        self.assertIsInstance(lm.category, list)

    @unittest.skip
    def test_luoo_page(self):
        luoo_page = app.LuooPage()
        latest_vol, page_num, vols = luoo_page.latest_vol, luoo_page.page_count, luoo_page.volumes
        self.assertIsNotNone(latest_vol and page_num and vols)
        self.assertIsInstance(page_num, int)
        self.assertIsInstance(latest_vol, dict)
        self.assertIsInstance(vols, list)

    @unittest.skip
    def test_luoo_vol(self):
        keys_should = ['cover', 'desc', 'pub_author', 'pub_date', 'tags', 'title', 'tracks', 'vol_index', 'vol_num']
        d = {
            "vol_index": 1276,
            "vol_num": "955",
            "title": "遗世而独立",
            "cover": "http://img-cdn2.luoo.net/pics/vol/59e97155ce4a9.jpg!/fwfh/640x452",
            "favor": 558,
            "comments": 51
        }
        luoo_vol = app.LuooVol(d)
        keys = list(luoo_vol.base.keys())
        keys.sort()
        self.assertListEqual(keys, keys_should)

    def test_luoo_vol_track(self):
        soup = BS('''
        <li class="track-item rounded" data-fav="0" id="track21611">
        <div class="track-wrapper clearfix">
        <span class="btn-control btn-play">
        <i class="icon-status-play"></i>
        <i class="icon-status-pause"></i>
        </span>
        <a class="trackname btn-play" href="javascript:;" rel="nofollow">01. Let Me In</a>
        <span class="artist btn-play">Basia Bulat</span>
        <a class="icon-info" data-sid="21611" data-sname="Let Me In" href="javascript:;" rel="nofollow"></a>
        <a class="btn-action-share icon-share" data-app="single" data-id="21611"
        data-img="http://img-cdn2.luoo.net/pics/albums/14277/59e8c59887ccb.jpg!/fwfh/580x580" data-text="推荐Basia
        Bulat的歌曲《Let Me In》（分享自@落网）" href="javascript:;" rel="nofollow">
        </a>
        <a class="btn-action-like icon icon-fav" data-cback="single_like_callback" data-from_id="1276"
        data-from_type="vol" data-id="21611" data-type="single" href="javascript:;" rel="nofollow">
        </a>
        </div>
        <div class="track-detail-wrapper" id="trackDetailWrapper21611">
        <div class="track-detail-arrow">
        <img src="http://s.luoo.net/img/trian.png"/>
        </div>
        <div class="track-detail rounded clearfix">
        <div class="player-wrapper">
        <img alt="Good Advice" class="cover rounded"
        src="http://img-cdn2.luoo.net/pics/albums/14277/59e8c59887ccb.jpg!/fwfh/580x580"/>
        <p class="name">Let Me In</p>
        <p class="artist">Artist: Basia Bulat</p>
        <p class="album">Album: Good Advice</p>
        </div>
        <div class="lyric-wrapper">
        <div class="lyric-content">
        </div>
        </div>
        </div>
        </div>
        <!--track-detail-wrapper end-->
        </li>
        ''', 'lxml')
        lvt = app.LuooVolTrack(soup)
        rs = {'cover': 'http://img-cdn2.luoo.net/pics/albums/14277/59e8c59887ccb.jpg!/fwfh/580x580',
              'name': 'Let Me In', 'artist': 'Basia Bulat', 'album': 'Good Advice'}
        self.assertDictEqual(lvt.meta, rs)


if __name__ == '__main__':
    unittest.main()
