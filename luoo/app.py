# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '18/10/2017 12:15 PM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''

import os
import sys
import requests
import time

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

# from bs4 import BeautifulSoup as BS
from logzero import logger as log
from tqdm import tqdm

from base.crawl import Crawl
from luoo import mge

# 期刊首页
URL_MUSIC = 'http://www.luoo.net/music'
URL_PTAG = 'http://www.luoo.net/tag/?p={}'

# 期刊具体卷
URL_VOLUME = 'http://www.luoo.net/vol/index/{}'
LUOO_LYRIC = 'http://www.luoo.net/single/lyric/'
LUOO_MP3 = 'http://mp3-cdn.luoo.net/low/luoo/radio{}/{}.mp3'


class LuooMusic(Crawl):
    """
    LuooMusic 与 LuooPage 的 page tag == 1的页面内容相同
    分析期刊首页内容, 获取如下信息
    {
        category: [],
        hot: [],
        pages: [],
    }
    """

    def __init__(self):
        Crawl.__init__(self)
        self.bs = None
        self.category = None
        self.hot = None
        self.page_count = 0
        # self.init()

    def init(self):
        self.bs = self.bs4get(URL_MUSIC)
        self.get_category()
        self.get_paginator()

    def get_category(self):
        """
            获取期刊类别
        [{'zh': '摇滚', 'href': 'http://www.luoo.net/music/rock'}, ...]

        :return:
        :rtype:
        """
        cat_raw = self.bs.find('div', 'pagenav-wrapper')
        cat = []
        for a in cat_raw.find_all('a'):
            hr = a.get('href')
            cat.append({
                'zh': a.text,
                'en': hr.split('/')[-1],
                'href': hr,
            })
        self.category = cat

    def get_hot(self):
        """
            获取最近热门期刊
        [{
            'href': 'http://www.luoo.net/vol/index/621',
            'name': '夏日小镇',
            'pic_src': 'http://img-cdn2.luoo.net/pics/vol/5376265ed8a1d.jpg!/fwfh/160x120',
            'favor': '24993人收藏'
        },...]
        :return:
        :rtype:
        """
        hot_raw = self.bs.find('div', 'widget-ct pic-widget')
        hot = []
        for itm in hot_raw.find_all('div', 'item'):
            vlink = itm.a
            vinfo = itm.find('div', 'info')
            hot.append({
                'href': vlink.get('href'),
                'name': vlink.img.get('alt'),
                'pic_src': vlink.img.get('src'),
                'favor': vinfo.p.text,
            })

        self.hot = hot

    def get_paginator(self):
        """获取期刊总页数

        :return:
        :rtype: int
        """
        _raw = self.bs.find('div', 'paginator')
        lks = _raw.find_all('a', 'page')
        self.page_count = max([int(x.text) for x in lks])


class LuooPage(LuooMusic):
    """ 1. 获取期刊某个页面所有期刊信息, 主要是 ``期刊的`` 卷标与 ``url检索值`` 不一致
        2. 获取单个期刊的评论与收藏

        注: 卷标是依次增长, 但索引值并不与其对应

    """

    def __init__(self, page_num=1):
        LuooMusic.__init__(self)
        self.bs = None
        # self.url = URL_PTAG.format(page_num)
        self.page_num = page_num
        self.volumes = None
        self.latest_vol = None
        self.init()

    def init(self):
        self.bs = self.bs4get(URL_PTAG.format(self.page_num))
        self.get_volumes()
        self.get_paginator()

    def get_volumes(self):
        """获取卷信息

        :return:
        :rtype:
        """
        vol_raw = self.bs.find('div', 'vol-list')
        vols = []
        for itm in vol_raw.find_all('div', 'item'):
            _img = itm.a.img
            _doc = itm.find('div', 'meta rounded clearfix')
            _idx, _num, _title = self.get_vol_index_num(_doc)
            _fv, _cm = self.get_favor_comment(_doc)
            vols.append({
                'vol_index': _idx,
                'vol_num': _num,
                'title': _title,
                'cover': _img.get('src'),
                'favor': _fv,
                'comments': _cm,
            })
        self.latest_vol = vols[0] if vols else {}
        self.volumes = vols

    @staticmethod
    def get_vol_index_num(doc):
        """
            返回 索引, 卷标, 卷名

        :param doc:
        :type doc:
        :return:
        :rtype:
        """
        _vol_txt = doc.a.text
        _vol_num = _vol_txt.split(' ')[0].split('.')[1]
        _raw = doc.a.get('href')
        _title = doc.a.get('title')
        return int(_raw.split('/')[-1]), _vol_num, _title

    @staticmethod
    def get_favor_comment(doc):
        """
            获取评论及收藏

        :param doc:
        :type doc:
        :return:
        :rtype:
        """
        _cmt = doc.find('span', 'comments')
        favs = doc.find('span', 'favs')

        return int(favs.text), int(_cmt.text)


class LuooVol(Crawl):
    """获取 volume 详细信息
    vol = {
        'num': 820,
        'tags': [''],
        'title': '',
        'cover': '',
        'desc': '',
        'pub_date': '',
        'tracks': {},
        'comments': {},
    }

    """

    def __init__(self, meta):
        Crawl.__init__(self)
        self.url = URL_VOLUME.format(meta.get('vol_index'))
        self.vol_index = meta.get('vol_index')
        self.bs = None
        self.base = {
            'vol_index': meta.get('vol_index'),
            'vol_num': meta.get('vol_num'),
            'title': meta.get('title'),
            'cover': meta.get('cover'),
        }

        self.init()

    def init(self):
        self.bs = self.bs4get(self.url)
        self.analyse()

    def analyse(self):
        self.get_tags()
        self.get_info()
        # self.get_comments()
        self.get_tracks()

    def get_tags(self):
        """获取该卷所属 tag 信息

        :return:
        :rtype:
        """
        tag_raw = self.bs.find('div', 'vol-tags clearfix')
        tags = []
        for itm in tag_raw.find_all('a', 'vol-tag-item'):
            tags.append(itm.text[1:])

        self.base['tags'] = tags

    def get_comments(self, page_num=1):
        """
        warn: 评论获取使用的是期刊卷的页面 ``索引值``

        :param page_num:
        :type page_num:
        :return:
        :rtype:
        """
        _url = 'http://www.luoo.net/comment/get/app/1/id/{}/commid/0/sort/new?p={}' \
            .format(self.vol_index, page_num)
        rs = requests.get(_url)
        self.base['comments'] = rs.json()

    def get_info(self):
        """
        vol = {
            'num': 820,
            'tags': [''],
            'title': '',
            'cover': '',
            'desc': '',
            'pub_date': '',
            'tracks': '',
        }
        :return:
        :rtype:
        """
        if not self.base.get('title'):
            _raw = self.bs.find('span', class_='vol-title')
            self.base['title'] = _raw.text

        if not self.base.get('cover'):
            _cover = self.bs.find(id='volCoverWrapper')
            self.base['cover'] = _cover.img.get('src')

        desc_raw = self.bs.find('div', 'vol-desc')
        # self.base['desc'] = str(desc_raw).replace('<br/>', '\n')
        self.base['desc'] = desc_raw.text

        self.base['pub_author'] = {
            'name': self.bs.find('a', 'vol-author').text,
            'link': self.bs.find('a', 'vol-author').get('href')
        }
        self.base['pub_date'] = self.bs.find('span', 'vol-date').text

    def get_tracks(self):
        """ 卷歌曲列表信息

        :return:
        :rtype:
        """
        tracks_raw = self.bs.find(id='luooPlayerPlaylist')
        track_list = []
        for t in tracks_raw.ul.find_all('li'):
            print('\n\n')
            print(t)
            print('\n\n')
            os._exit(-1)
            if t.get('id'):
                _t_name = t.find('a', 'trackname btn-play')
                t_pos = _t_name.text.split('.')[0]
                t_id = t.get('id')[len('track'):]
                _track = {
                    'stream_name': t_pos,
                    'track_id': int(t_id),
                }
                _track = dict(_track, **LuooVolTrack(t).meta)
                track_list.append(_track)

        self.base['tracks'] = track_list


class LuooVolTrack(object):
    """解析 volume tracks 信息
    track = {
        'cover': '',
        'name': '',
        'artist': '',
        'album': '',
        'lyric': '',
    }
    """

    def __init__(self, doc):
        self.meta = {}
        self.doc = doc
        self.get_meta()

    def get_meta(self):
        _raw = self.doc.find('div', 'player-wrapper')
        self.meta = {
            'cover': _raw.img.get('src'),
            'name': _raw.find('p', 'name').text.lstrip(),
            'artist': ''.join(_raw.find('p', 'artist').text.split(':')[1:]).lstrip(),
            'album': ''.join(_raw.find('p', 'album').text.split(':')[1:]).lstrip(),
        }


class LuooMusicCrawl(object):
    def __init__(self, job_cfg=None):
        job_cfg = job_cfg or {}
        if job_cfg.get('update', True):
            self.update_newest_music_volumes()

    def update_newest_music_volumes(self):
        """
        检查期刊页面的 ``期刊卷信息``
        如果提供 page 页面, 则强制检查指定页面
        否则, 则依据最新页面信息来检查

        :return:
        :rtype:
        """
        all_vols = self.get_newest_vols()
        self.init_vol_to_crawl_tb(all_vols)

    def update_volumes_by_page(self, page_num, start='', end=''):
        """
        从 page_num 页面获取所有 vols
        所有大于等于 start, 并且小于 end 的 vol 都会被添加到数据库中

        :param page_num:
        :type page_num:
        :param start:
        :type start:
        :param end:
        :type end:
        :return:
        :rtype:
        """
        luoo_p = LuooPage(page_num)
        luoo_p.get_volumes()
        vols = luoo_p.volumes

        def is_ok(vol):
            b = True
            if start:
                b &= vol.get('vol_num', '000') >= start
            if end:
                b &= vol.get('vol_num', '000') < end
            if b:
                return vol

        tags = list(filter(is_ok, vols))
        self.init_vol_to_crawl_tb(tags)

    @staticmethod
    def get_newest_vols():
        # 从数据库取出爬取成功的最后一组数据的卷信息
        vol_curr = mge.MusicVolumes.objects.only('vol_num').first()

        # 获取卷标
        vol_curr = vol_curr.vol_num if vol_curr else '000'
        # if not vol_curr:
        #     vol_curr = '000'
        # else:
        #     vol_curr = vol_curr.vol_num
        # luoo.net 最新 vol 的值

        luoo_page = LuooPage()
        latest_vol, page_num = luoo_page.latest_vol, luoo_page.page_count

        # 如果卷标相同, 则忽略更新数据库
        if latest_vol.get('vol_num') <= vol_curr:
            log.debug(':) got all music, skip crawl from luoo.net.')
            return

        all_vols = []
        # 页面索引值最小的, 期刊最新
        for p in range(page_num + 1):
            luoo_p = LuooPage(p)
            luoo_p.get_volumes()
            # vol_curr = '000'

            # 过滤符合条件的所有页面
            tags = list(filter(
                lambda s: vol_curr < s.get('vol_num', '000') <= latest_vol.get('vol_num'),
                luoo_p.volumes
            ))
            all_vols += tags
            log.debug('page ({}/{}/{}) done'.format(p, len(luoo_p.volumes), len(tags)))

            # 如果计数小于 page size, 则已经遍历满足条件的所有vol
            if len(tags) != len(luoo_p.volumes):
                break

        return all_vols

    @staticmethod
    def init_vol_to_crawl_tb(vols):
        """ 存储爬取到的 vol 概要信息到数据库, 为后期爬取详情做准备

        :return:
        :rtype:
        """
        if not vols:
            return
        for vol in vols:
            mge.save_music_volumes(vol)
            log.debug('[done] {}'.format(vol.get('vol_num')))

    @staticmethod
    def get_missed_vol(alls):
        alls = list(set(alls))
        alls.sort()
        i = 1
        for x in alls:
            x = int(x)
            if i != x:
                print('missed vol ({}~{})'.format(i, x))
                i = x
            i += 1

    def find_missed_vols(self):
        """
            检查 luoo.net 不存在的卷

        :return:
        :rtype:
        """
        vols = mge.MusicVolumes.objects().order_by('vol_num').all()
        ar = [d['vol_num'] for d in vols]
        self.get_missed_vol(ar)

    @staticmethod
    def save_volume_tracks(d):
        p = LuooVol(d)
        mge.save_volumes(p.base)
        return True

    def start_crawl_volumes(self, start_index='', count=0):
        """
            从 start_index 开始, 共爬取多少记录

        :param start_index:
        :type start_index:
        :param count:
        :type count:
        :return:
        :rtype:
        """
        # 从详情获取最后一个爬取的卷标
        done_vols = mge.Volumes.objects.order_by('-vol_num').first()
        last_vol = done_vols.vol_num if done_vols else '000'

        # 从概要卷获取未爬取的卷标
        vols = mge.MusicVolumes.objects(vol_num__gt=start_index or last_vol).order_by('vol_num').all()
        if not vols:
            log.info(':) got all volumes, skip crawl from luoo.net.')
            return

        _count = 0
        log.debug('try crawl about {} volumes'.format(len(vols)))
        for vol in tqdm(vols, ascii=True, desc=''):
            d = {
                'vol_index': vol.vol_index,
                'vol_num': vol.vol_num,
                'title': vol.title,
                'cover': vol.cover,
            }

            if self.save_volume_tracks(d):
                log.debug('Fetch ({}/{}) done'.format(d['vol_index'], d['vol_num']))
            else:
                log.error('Failed ({}/{})'.format(d['vol_index'], d['vol_num']))

            _count += 1
            time.sleep(0.5)
            if count and _count > count:
                break


def run():
    lmc = LuooMusicCrawl()
    # lmc.start_crawl_volumes()
    lmc.find_missed_vols()


if __name__ == '__main__':
    run()
