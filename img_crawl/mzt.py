# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '26/10/2017 9:46 AM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''

import os
import sys
import re
import json
import time
from urllib.parse import urljoin
from multiprocessing import Pool, cpu_count

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import bs4
from logzero import logger as log
from tqdm import tqdm
import click

from izen import helper

from base import abc
from base.abc import cfg

from base.crawl import Crawl

M = {
    'index': 'http://www.mzitu.com',
    'all': 'http://m.mzitu.com/all',
    'page': 'http://m.mzitu.com/',
    'tag': 'http://m.mzitu.com/tag/{}/page/{}',
    'image': '',
}
cache_index = 1
finished = []


class Mz(Crawl):
    def __init__(self, base_dir='/tmp/mzt', parser='lxml'):
        """
            初始化本地目录
        """
        Crawl.__init__(self, M['index'])
        self.all_indexes = None
        self.archives = None
        self.archive = None
        self.base_dir = base_dir
        self.parser = parser
        # self.single_page()
        return
        # if update:
        #     self.get_all()
        # self.use_cache()

    def use_cache_indexes(self):
        self.all_indexes = json.loads(helper.read_file('mz.idx.json').decode())

    def use_cache(self):
        self.archives = json.loads(helper.read_file('mz.json').decode())

    def single_page(self):
        self.archive = {
            'ym': '201710',
            'md': '1026',
            'title': 'TEST',
            'url': ' http://m.mzitu.com/106936'
        }
        t, src_, name, _ = self.get_single_page_total(self.archive['url'])
        self.archive['total'] = t
        self.archive['img_src'] = src_

    def get_all(self):
        """
        dat = {
            '201710': [{
                'archive_time': '1025',
                'title': '',
                'url': '',
            }, ...],
            '201709': [{
                'archive_time': '0910',
            }, ...],
        }

        :return:
        :rtype:
        """
        raw = self.bs4get(M['all'])
        archives = raw.find(id='post-archives')
        print(len(archives))
        dat = []
        all_indexes = []
        ym = ''
        for arc in archives:
            if not isinstance(arc, bs4.element.Tag):
                continue

            cls_type = arc.get('class')[0]

            if cls_type == 'archive-header':
                ym = self.analy_header(arc)
                continue
            d = self.analy_brick(arc)
            all_indexes.append(d['url'])
            d['ym'] = ym
            dat.append(d)

        self.all_indexes = all_indexes
        # abc.write_file(json.dumps(dat).encode(), 'mz.json')

    def only_fetch_latest(self):
        self.use_cache_indexes()
        done = self.all_indexes
        self.get_all()
        # abc.write_file(json.dumps(all_indexes).encode(), 'mz.idx.json')
        _nv = list(set(self.all_indexes) - set(done))
        log.debug('Not Download: {}'.format(','.join(_nv)))
        for x in _nv:
            self.download_by_index(x)

    def get_tag_indexes(self, tag_url):
        raw = self.bs4get(tag_url)
        content = raw.find('div', id='content')
        h2s = content.find_all('h2')
        tags = []
        for art in h2s:
            if not isinstance(art, bs4.element.Tag):
                continue
            rs = art.a.get('href').split('/')[-1]
            tags.append(rs)
        return tags

    def get_hot_indexes(self, url):
        pass

    @staticmethod
    def analy_header(doc):
        txt = doc.text
        _y, _m = txt.split('-')
        _y = re.sub('\D', '', _y)
        _m = re.sub('\D', '', _m).zfill(2)
        return _y + _m

    @staticmethod
    def analy_brick(doc):
        title = doc.text
        href = doc.a.get('href').split('/')[-1]
        archive_time = doc.find('span', 'archive-time').text
        md = [x.zfill(2) for x in archive_time.split('-')]
        return {
            'md': ''.join(md),
            'title': title,
            'url': href,
        }

    def get_single_page_total(self, url):
        raw = self.bs4get(url)
        try:
            _pub_time = raw.find('span', 'time').text
            _pub_time = _pub_time.split(' ')[0].split('-')
            _y, t = _pub_time[0], ''.join(_pub_time[1:])

            _total = raw.find('span', 'prev-next-page').text
            _total = re.sub('\D', '', _total.split('/')[1])

            figure = raw.find('figure')
            src = figure.p.a.img.get('src')
            alt = figure.p.a.img.get('alt')
            return {
                'total': int(_total),
                'img_src': src,
                'time': '{}/{}'.format(_y, t),
                'name': alt.encode(),
            }
        except AttributeError as e1:
            log.error('got from ({}) {}'.format(url, e1))

    def get_page_by_index(self, index):
        # _url = '{}{}'.format(M['page'], index)
        _url = urljoin(M['page'], index)
        return self.get_single_page_total(_url)

    def download_by_index(self, index):
        global cache_index
        global finished

        _e_list1 = ['33201', '34949', '35850', '45364', '47526']

        if not index:
            log.info('no index found...')
            return

        dat = self.get_page_by_index(index)
        if not dat:
            log.error('fail@none: {}'.format(index))
            return

        try:
            # 扩展名, 文件夹名, 自增名, 图片固定url
            _ext = dat['img_src'].split('.')[-1]
            _name_off = 3 + len(_ext)
            if index in _e_list1:
                _name_off = 4 + len(_ext)
            img = dat['img_src'][:-_name_off]

            if index == '54856':
                _name_pre = ''
                fd_img = 'a'
            elif index in _e_list1:
                fd_img, _ = get_fd_name(dat['img_src'])
                _name_pre = ''
            else:
                _name_pre = img.split('/')[-1]
                fd_img = img[-1]
            _path_local = os.path.join(dat['time'], fd_img)

            fd = os.path.join(self.base_dir, _path_local)
            helper.mkdir_p(fd, True)
            os.chdir(fd)

            if index in _e_list1:
                _img_fmt = '{}{}1.{}'
            else:
                _img_fmt = '{}{}.{}'

            params = [
                {
                    'img_url': _img_fmt.format(img, str(x + 1).zfill(2), _ext),
                    'title': '{}-{}{}.{}'.format(
                        dat['name'].decode(),
                        _name_pre,
                        str(x + 1).zfill(2),
                        _ext,
                    )
                }
                for x in range(dat['total'])
            ]

            _fail_count = 0
            for para in tqdm(params, ascii=True, desc='%8s ✈ %10s' % (index, _path_local)):
                rs = self.download_and_save(para)
                if rs == self.save_status['fail']:
                    _fail_count += 1
                    time.sleep(0.5)
                elif rs == self.save_status['ok']:
                    time.sleep(1.5)
                elif rs == self.save_status['skip']:
                    # 如果本地文件已存在, 则不进行等待
                    time.sleep(0.0001)

                if _fail_count > 5:
                    log.warn('fail@5 img of this, skip({}) => ({})'.format(index, _path_local))
                    break

            cache_index += 1
            finished.append(index)
            helper.write_file(json.dumps(finished), '/tmp/mz.done')
            log.warn('Done:({}/{})'.format(cache_index, index))
        except TypeError as _:
            log.error('fail@type: {}'.format(index))

    def download_by_tag(self, tag):
        i = 0
        while True:
            i += 1
            tag_url = M['tag'].format(tag, i)
            idxs = self.get_tag_indexes(tag_url)
            print(idxs)
            time.sleep(0.2)
            if not idxs:
                break

                # pool = Pool(processes=cpu_count())
                # pool.map(self.download_by_index, idxs)

    def download_by_hot(self):
        pass


@click.command()
@click.option('--max_proc', '-m',
              type=int,
              help='the max proc used\nUSAGE: <cmd> -m <num>')
@click.option('--update', '-u',
              is_flag=True,
              help='update local cache\nUSAGE: <cmd> -u')
@click.option('--newest', '-n',
              is_flag=True,
              help='update local cache and fetch newest\nUSAGE: <cmd> -n')
@click.option('--which', '-w',
              help='the index to download\nUSAGE: <cmd> -w <index,index1,...>')
@click.option('--pic_idx', '-p',
              help='the pic_idx\nUSAGE: <cmd> -p <index>')
@click.option('--base_dir', '-d',
              help='the dir to store images\nUSAGE: <cmd> -d <dir_pth>')
@click.option('--offset', '-o',
              type=int,
              help='the position of list\nUSAGE: <cmd> -o <offset>')
@click.option('--total', '-t',
              type=int,
              help='the total nums to download\nUSAGE: <cmd> -t <num>')
@click.option('--clear', '-c',
              is_flag=True,
              help='clear 0-byte file')
def run(pic_idx, offset, clear, max_proc, update, which, total, base_dir, newest):
    can_clear = False

    if base_dir:
        can_clear = True
        abc.update_cfg('mzt.base_dir', base_dir)
    else:
        base_dir = cfg.get('mzt.base_dir')

    mz = Mz(base_dir=base_dir)
    if newest:
        mz.only_fetch_latest()
        return

    if which:
        log.debug('download <{}>'.format(which))
        for w in which.split(','):
            mz.download_by_index(w)
        return

    if update:
        log.debug('update local cache')
        mz.get_all()
        return

    if clear:
        if not can_clear:
            log.error('you must give base_dir to clear 0-byte images.')
            return
        log.debug('do clear empty image files.')
        mz.clear_empty_img(base_dir, do_clear=False)
        return

    mz.use_cache_indexes()

    start_index = 0
    if pic_idx:
        start_index = mz.all_indexes.index(pic_idx)
    if offset:
        start_index = int(offset)

    end_index = -1
    if total:
        end_index = start_index + total
    all_idx = mz.all_indexes[start_index:end_index]

    _m = max_proc if max_proc else cpu_count()
    pool = Pool(processes=_m)
    pool.map(mz.download_by_index, all_idx)


def get_fd_name(uri):
    title, ext = uri.split('/')[-1].split('.')
    print(ext)

    _ = ''
    for x in title:
        if not x.isdigit():
            _ += x

    i = title.find(_)
    return _, title[i + len(_):-1]


if __name__ == '__main__':
    pass
    run()
    # wr = 'http://i.meizitu.net/2014/11/25t011.jpg'
    # s = get_fd_name(wr)
    # print(s)
