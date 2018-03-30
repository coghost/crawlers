# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '01/11/2017 10:04 AM'
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
from urllib.parse import urljoin
from multiprocessing import Pool

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

'''
small: http://44.style/a-9453/
big: http://44.style/a-9453-b/
1. 获取所有 tags
2. 某个 tag
3. 该 tag 对应的所有页面 `page`
4. 某 page 下的所有图片
'''

from logzero import logger as log
from tqdm import tqdm
import click

from base.crawl import Crawl
from base import abc
from base.abc import cfg
from izen import helper

dir_pre = ''
D = {
    'index': 'http://44.style/',
    'tags': 'http://44.style/tags/',
    'page_suffix': '-b/',
}


class D4(Crawl):
    def __init__(self, base_dir='/tmp/d4', parser='html.parser', encoding="GBK"):
        """
            初始化本地目录
        44.style: support html.parser
        """
        Crawl.__init__(self, encoding=encoding)
        self.base_dir = base_dir
        self.parser = parser
        self.all_tags = None
        self.t2i = {}
        self.i2t = {}

    def load_cache(self):
        self.all_tags = json.loads(helper.read_file('d4.tags.json'))
        self.t2i = json.loads(helper.read_file('d4.t2i.json'))
        self.i2t = json.loads(helper.read_file('d4.i2t.json'))

    def update_reverse_cached(self):
        # dat = json.loads(helper.read_file('d4.4.t2i.json'))
        rs_dat = {}
        for k, v in self.t2i.items():
            d = dict(zip(v, [k for _ in v]))
            rs_dat = dict(rs_dat, **d)

        if rs_dat:
            self.i2t = rs_dat
            # helper.write_file(json.dumps(self.i2t).encode(), 'd4.i2t.json')

    def get_tag_position(self, idx, idx_s=4, is_tag=True):
        all_tags = self.all_tags[idx_s]
        if not is_tag:
            idx = self.get_index_name_by_tag(idx)
            print(idx)
        for si, t in enumerate(all_tags):
            if t['src'] == idx:
                return si

    def get_index_name_by_tag(self, page_idx):
        """
            依据 index 值, 来反向获取对应 按名字分类的 tag 值

        :return:
        :rtype:
        """
        if not self.i2t:
            self.i2t = json.loads(helper.read_file('d4.i2t.json'))

        return self.i2t.get(page_idx)

    def update_tags(self):
        """
            更新 44.style 的所有 tags 到本地缓存.

        :return:
        :rtype:
        """
        tags_root = []
        tags_raw = self.bs4get(D['tags'])
        if not tags_raw:
            log.error('cannot update tags.')
            return

        tagall = tags_raw.find_all('div', class_='tagall photo')
        for tag in tagall:
            tag_in = []
            ul_li = tag.ul.find_all('li')
            if ul_li:
                for li in ul_li:
                    tag_in.append({
                        'src': li.a.get('href'),
                        'name': li.a.text,
                    })
            tags_root.append(tag_in)

        if tags_root:
            helper.write_file(json.dumps(tags_root).encode(), 'd4.tags.json')

    def gen_tags2index(self, idx=4):
        """
            生成 tag 对 tag 页面索引的对应

        :param idx:
        :type idx:
        :return:
        :rtype:
        """
        self.load_cache()
        tags = self.all_tags[idx]

        for tag in tqdm(tags, ascii=True):
            self.update_tag_pages_cache(tag)

    @staticmethod
    def trim_last_slash(url):
        if url[-1] == '/':
            url = url[:-1]
        return url

    @staticmethod
    def gen_fd_by_tag(tag_idx):
        t = tag_idx.replace('/', '')
        t = t.replace('-', '')
        return t

    def update_tag_pages_cache(self, tag):
        """
            更新tag对应页面到本地缓存

        :param tag:
        :type tag:
        :return:
        :rtype:
        """
        _k = tag['src']
        if tag['src'] in json.loads(helper.read_file('d4.t2i.json')):
            log.debug('{} already got'.format(tag['src']))
            return

        pages = self.fetch_tags_pages_by_index(tag['src'])
        self.t2i[_k] = pages

        helper.write_file(json.dumps(self.t2i).encode(), 'd4.t2i.json')

    def fetch_tags_pages_by_index(self, tag_index):
        """
            获取 tag 对应页面的所有索引

        :param tag_index:
        :type tag_index:
        :return:
        :rtype:
        """
        pages = []
        _url = self.trim_last_slash(urljoin(D['index'], tag_index))

        pages_raw = self.bs4get(_url)
        if not pages_raw:
            log.error('fail-tpbi @ {}'.format(tag_index))
            return pages

        num_raw = pages_raw.find('div', id='pagenum')
        num_p = num_raw.find_all('li')[0].text

        total_num = int(num_p.split('/')[1])
        all_pages = [
            _url + '-{}'.format(x + 1)
            for x in range(total_num)
        ]

        for page_ in tqdm(all_pages, ascii=True, leave=False):
            pages += self.fetch_page_links(page_)
        return pages

    def fetch_page_links(self, page_url):
        """
            获取页面内子链接内容.

        :param page_url:
        :type page_url:
        :return:
        :rtype:
        """
        tag_all_pages = []
        try:
            _raw = self.bs4get(page_url)
            _list_pics = _raw.find('div', id='list-pic')
            _items = _list_pics.find_all('div', 'item')
            for itm in tqdm(_items, ascii=True, leave=False):
                _img_raw = itm.find('div', 'img')
                src = self.trim_last_slash(_img_raw.a.get('href'))
                src += '-b/'
                tag_all_pages.append(src)
        except AttributeError as e:
            log.warn('fail-tp @ {}'.format(page_url))
        finally:
            return tag_all_pages

    def download_only_from_index(self, page_index):
        """
            只使用 下载页面的 page_index 来下载
            > 如果可以查找到页面对应的上级 tag, 则下载
            > 否则, 需要先更新本地 tags

        :param page_index:
        :type page_index:
        :return:
        :rtype:
        """
        fd = self.get_index_name_by_tag(page_index)
        if not fd:
            log.error('{} has not tag, run update tags first'.format(page_index))
        else:
            log.debug('tag folder is: {}'.format(fd))

    def download_by_tag(self, tag_idx, down=True):
        """
            从tag开始,依次下载所有页面

        :param tag_idx:
        :type tag_idx:
        :return:
        :rtype:
        """
        if not self.t2i:
            self.load_cache()

        pages = self.t2i[tag_idx]
        if not down:
            print(pages)
            os._exit(-1)
        log.debug('total ({})'.format(len(pages)))

        pool = Pool(processes=8)
        pool.map(self.download_by_index, pages)

    def download_by_index(self, page_index):
        """
            依据页面索引, 开始下载

        :param page_index:
        :type page_index:
        :return:
        :rtype:
        """
        # 依据 tag+page 索引值来生成存储目录, 保证不会下载相同页面
        fd_u = self.get_index_name_by_tag(page_index)
        fd_u = self.gen_fd_by_tag(fd_u)

        fd = self.gen_fd_by_tag(page_index)
        if dir_pre:
            _base_dir = self.base_dir + '001'
        else:
            _base_dir = self.base_dir
        fd_abs = os.path.join(_base_dir, dir_pre, fd_u, fd)

        if not os.path.exists(fd_abs):
            os.makedirs(fd_abs)
        os.chdir(fd_abs)

        _url = self.trim_last_slash(urljoin(D['index'], page_index))
        _raw = self.bs4get(_url)
        if not _raw:
            log.error('fail-bi @ {}'.format(page_index))
            return

        b_all_list = _raw.find('div', id='b_all_list')
        itembls = b_all_list.find_all('div', 'itembl')

        params = [
            {
                'img_url': 'http:{}'.format(item.a.img.get('data-original')),
                'title': '{}.{}'.format(
                    item.a.img.get('alt'),
                    item.a.img.get('data-original').split('.')[-1]),
            }
            for item in itembls
        ]

        _fail_count = 0
        for para in tqdm(params, ascii=True, desc='%8s ✈ %10s' % (page_index, fd)):
            rs = self.download_and_save(para)
            if rs == self.save_status['fail']:
                _fail_count += 1
                time.sleep(0.5)
            elif rs == self.save_status['ok']:
                # 如果成功, 则重置计数.
                _fail_count = 0
                time.sleep(1)
            elif rs == self.save_status['skip']:
                # 如果本地文件已存在, 则不进行等待
                time.sleep(0.0001)

            # 如果一个页面内有连续超过5个链接不能下载,则认为页面失效, 不再下载.
            if _fail_count > 5:
                log.warn('fail@5 img of this, skip({}) => ({})'.format(page_index, fd))
                break

    def download_by_name(self, tag):
        self.download_by_tag(tag['src'])


@click.command()
@click.option('--name', '-n',
              help='the name of artist\nUSAGE: <cmd> -n <name>')
@click.option('--tag2name', '-tn',
              help='use tag to find name of artist\nUSAGE: <cmd> -tn <tag_idx>')
@click.option('--base_dir', '-d',
              help='the dir to store images\nUSAGE: <cmd> -d <dir_pth>')
@click.option('--update', '-u',
              is_flag=True,
              help='update local cache\nUSAGE: <cmd> -u')
@click.option('--tag_group', '-tg',
              type=int,
              default=4,
              help='the tag group\nUSAGE: <cmd> -tg <num>')
@click.option('--tag_idx', '-ti',
              help='the tag_idx\nUSAGE: <cmd> -ti <index>')
@click.option('--from_tag_idx', '-fti',
              help='download from the tag_idx\nUSAGE: <cmd> -fti <index>')
@click.option('--from_page_idx', '-fpi',
              help='download from the page_idx\nUSAGE: <cmd> -fpi <index>')
@click.option('--total', '-t',
              type=int,
              help='the total nums to download\nUSAGE: <cmd> -t <num>')
@click.option('--page_idx', '-p',
              help='the page_idx\nUSAGE: <cmd> -p <index>')
@click.option('--clear', '-c',
              is_flag=True,
              help='clear 0-byte file')
def run(tag_group, page_idx, tag_idx,
        name, tag2name,
        from_tag_idx, from_page_idx,
        total, clear, update, base_dir):
    global dir_pre
    if base_dir:
        abc.update_cfg('d4.base_dir', base_dir)
    else:
        base_dir = cfg.get('d4.base_dir')

    # 初始化存储目录
    d4 = D4(base_dir)
    d4.load_cache()
    tags = d4.all_tags[tag_group]

    if update:
        log.debug('update local cache')
        d4.update_tags()
        return

    if clear:
        log.debug('do clear empty image files.')
        d4.clear_empty_img(base_dir, do_clear=False)
        return

    if tag_idx:
        d4.download_by_tag(tag_idx, down=False)
        return

    if from_page_idx:
        idx = d4.get_tag_position(from_page_idx, tag_group, False)
        print(idx)
        return

    if from_tag_idx:
        idx = d4.get_tag_position(from_tag_idx, tag_group)
        print(idx)
        return

    if page_idx:
        d4.download_only_from_index(page_idx)
        return

    current = cfg.get('d4.tag_index', 0)

    max_t = -1
    if total:
        max_t = current + total

    if tag2name:
        for t in tags:
            # tidx = d4.gen_fd_by_tag(t['src'])
            if t.get('src') == tag2name:
                print(t)
                os._exit(-1)

    if name:
        dir_pre = name
        for t in tags:
            if t.get('name') == name:
                d4.download_by_name(t)
                break
        # log.error('no data by name({})'.format(name))
        return

    for tag in tags[current:max_t]:
        log.debug('Try:{} @ {}'.format(current, tag['src']))
        d4.download_by_tag(tag['src'])
        log.info('DONE@{}'.format(tag['src']))
        current += 1
        abc.update_cfg('d4.tag_index', current)
        time.sleep(1)


if __name__ == '__main__':
    run()
