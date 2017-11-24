# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '24/10/2017 11:44 AM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''

import os
import sys
import time
from multiprocessing import Pool, cpu_count
import re

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import bs4
from logzero import logger as log
from tqdm import tqdm
import click

from base import abc
from base.crawl import Crawl

MJ = {
    'index': 'http://www.mmjpg.com',
    'home': 'http://www.mmjpg.com/home/{}',
    'hot': 'http://m.mmjpg.com/hot/',
    'hot_page': 'http://m.mmjpg.com',
    'hot_more': 'http://m.mmjpg.com/getmore.php?te=2&page={}',
    'top': '',
    'more': '',
}

headers = {
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/56.0.2924.87 Safari/537.36',
    'Referer': "http://www.mmjpg.com"
}

crawl_to = 5
max_page_num = 115
hot2fd = 1


def gen_fd_from_image_url(img_):
    """
        从 url 获取图片的日期做为存储路径

    :param img_:
    :type img_:
    :return:
    :rtype:
    """
    re_ = re.compile(r'\d+?/\d+')
    _name = re_.findall(img_)
    if _name:
        return _name[0]


class Mj(Crawl):
    def __init__(self, base_dir):
        Crawl.__init__(self, MJ['index'])
        self.base_dir = base_dir

    def get_hot(self):
        """
            this is the default page of hot, samed as get_hot_page = 1+2

        :return:
        :rtype:
        """
        _url = MJ['hot']
        hot = self.bs4get(_url)
        articles = hot.find('ul', class_='article')
        hots = self.analy_hot(articles)
        return hots

    @staticmethod
    def analy_hot(articles, prefix=''):
        """
            解析获取相应名称与 ``链接``

        :param articles:
        :type articles:
        :param prefix:
        :type prefix:
        :return:
        :rtype:
        """
        hots = []
        for art in articles:
            h2_raw = art.find('h2')
            if not isinstance(h2_raw, bs4.element.Tag):
                continue
            img_info = h2_raw.a
            hots.append({
                'title': img_info.text,
                'url': prefix + img_info.get('href'),
            })

        return hots

    def get_hot_page(self, img_url):
        _pre = MJ['hot_page']
        _raw = self.bs4get(img_url)
        articles = _raw.find_all('li')
        hots = self.analy_hot(articles, prefix=_pre)

        return hots

    def get_hot_max_num(self):
        """
            获取依据 hot 分类的最大的页面数

        :return:
        :rtype:
        """
        _url = MJ['hot_more']
        idx = 100
        while True:
            c = self.bs4get(_url.format(idx))
            if not len(c):
                print(idx, 'exit')
                os._exit(-1)
            else:
                print(idx, 'done')
            idx += 1
            time.sleep(0.1)

    def get_artist_info(self, url=''):
        """
            url = '{}/853'.format(glb_img_url)

            返回 img_url, total_num

        :param url:
        :type url:
        :return:
        :rtype:
        """
        if not url:
            return

        raw = self.bs4get(url)
        cpg = raw.find('div', 'contentpage')
        _total = self.get_image_total(cpg)

        img_url_raw = raw.find('div', 'content')
        iu = img_url_raw.find('a')
        _img_url = '/'.join(iu.img.get('src').split('/')[:-1])
        _img_url += '/{}.jpg'

        return _img_url, _total

    @staticmethod
    def get_image_total(cpg):
        """
            解析获取最大页面数

        :param cpg:
        :type cpg:
        :return:
        :rtype:
        """
        _r = re.compile(r'\d*\)')
        _total = 0
        for c in cpg.children:
            if c.i:
                _n = re.findall(_r, c.i.text)
                if _n:
                    _total = int(_n[0][:-1])
                    break
        return _total

    def download_image(self, params):
        """
            下载相应图片
        :param params:
        :type params: dict
        :return:
        :rtype:
        """
        img_url, title = params.get('img_url'), params.get('title')

        filename = '{}'.format(img_url.split('/')[-1])
        filename = filename.split('.')[0].zfill(2)

        _img_fd = gen_fd_from_image_url(img_url)
        _rel_pth = '{}/{}.jpg'.format(_img_fd, filename)
        fpth = '{}/{}/{}-{}.jpg'.format(self.base_dir, _img_fd, title, filename)

        if abc.is_file_ok(fpth):
            return

        if os.path.exists(fpth):
            log.debug('RETRY: ({})'.format(_rel_pth))
        else:
            abc.mkdir_p(fpth)

        img = self.crawl(img_url)
        if not img:
            return
        with open(fpth, 'wb') as f:
            f.write(img)

    def download_and_save(self, params, force_write=False):
        img_url, title = params.get('img_url'), params.get('title')

        # 给 小于 10 的名字补 0
        filename = '{}'.format(img_url.split('/')[-1])
        filename = filename.split('.')[0].zfill(2) + '.jpg'
        filename = '{}-{}'.format(title, filename)

        if not force_write and abc.is_file_ok(filename):
            return 0

        img = self.crawl(img_url)
        if not img:
            return 1
        with open(filename, 'wb') as f:
            f.write(img)
        return 3

    def update_idx_map(self, img_url):
        """
            update hot index to folder map

        :param img_url:
        :type img_url:
        :return:
        :rtype:
        """
        global hot2fd
        _img_fd = gen_fd_from_image_url(img_url)
        print('{} > {}'.format(hot2fd, _img_fd))

    def multi_get(self, start_index=1, end_index=1):
        start_index = start_index if start_index else 1

        for page_idx in range(start_index, max_page_num):
            self.single_get(page_idx)
            log.debug('DONE@: {}'.format(page_idx))

            page_idx += 1
            if page_idx >= end_index:
                break
            time.sleep(5)

    def single_get(self, page_idx):
        _url = MJ['hot_more'].format(page_idx)
        arts = self.get_hot_page(_url)

        pool = Pool(processes=cpu_count())
        pool.map(self.get_art, arts)

    def get_art(self, art):
        url_, t = self.get_artist_info(art['url'])

        _img_fd = gen_fd_from_image_url(url_)
        fd = os.path.join(self.base_dir, _img_fd)
        abc.mkdir_p(fd, True)
        os.chdir(fd)

        params = [
            {
                'title': art['title'],
                'img_url': url_.format(_ + 1),
            }
            for _ in range(t)]

        _fail_count = 0
        for pam in tqdm(params, ascii=True, desc='%10s' % _img_fd, leave=False):
            rs = self.download_and_save(pam)
            if rs == 1:
                _fail_count += 1
                time.sleep(0.5)
            elif rs == 3:
                time.sleep(1.5)
            else:
                # 如果本地文件已存在, 则不进行等待
                time.sleep(0.0001)
            if _fail_count > 5:
                log.warn('skip({}) => ({})'.format(_img_fd, url_))
                break


@click.command()
@click.option('--pos', '-p',
              nargs=2, type=int,
              help='the start and end page index\nUSAGE: <cmd> -p 1 3')
@click.option('--clear', '-c',
              is_flag=True,
              help='clear 0-byte file')
@click.option('--base_dir', '-d',
              help='the dir to store images\nUSAGE: <cmd> -d <index>')
def run(pos, clear, base_dir):
    start, end = pos
    log.debug('fetch {}~{}'.format(start, end))
    can_clear = False
    if not base_dir:
        base_dir = '/tmp/mzt/'
    else:
        can_clear = True

    mj = Mj(base_dir)
    if clear:
        if not can_clear:
            log.error('you must give base_dir to clear 0-byte images.')
            return
        log.debug('do clear empty image files.')
        mj.clear_empty_img(base_dir)
        return
    mj.multi_get(start, end)


if __name__ == '__main__':
    run()
