# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '06/11/2017 12:27 PM'
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
from urllib.parse import urljoin, urlencode
import re

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

M = {
    'index': 'http://yxpjw.me',
    'search': 'http://yxpjw.me/plus/search.php',
}


class Pjw(Crawl):
    def __init__(self, base_dir='/tmp/d4'):
        Crawl.__init__(self, refer=M['index'])
        self.base_dir = base_dir
        self.store = {}

    def load_store(self):
        self.store = json.loads(abc.read_file('pjw.json'))

    def update_store(self, key, val):
        self.store[key] = val
        abc.write_file(json.dumps(self.store).encode(), 'pjw.json')

    def get_all_imgs(self, page_url, run_alone=False):
        """
        1: http://yxpjw.me/luyilu/2017/1105/4149.html t=6
        2:
        :return:
        :rtype:
        """
        page_raw = self.bs4get(page_url)
        if not page_raw:
            log.error('cannot download from `{}`'.format(page_url))
            return
        content = page_raw.find('div', 'content')
        title, total = self.analy_page_title(content)
        imgs = self.analy_page_image_links(content)
        size = len(imgs)
        page_total = total // size
        page_all_sub_urls = [
            '{}_{}.html'.format(page_url.replace('.html', ''), i + 2)
            for i in range(page_total)
            ]
        # print(page_all_sub_urls)
        if run_alone:
            pool = Pool(processes=8)
            results = []
            for _url in page_all_sub_urls:
                rs = pool.apply_async(self.fetch_page_image_links, (_url,))
                results.append(rs)

            for r in results:
                imgs += r.get()
        else:
            for _url in page_all_sub_urls:
                imgs += self.fetch_page_image_links(_url)

        print(json.dumps(imgs, indent=2))
        return title, imgs

    def analy_page_title(self, doc):
        if not doc:
            return '', 0

        def ab(txt):
            # re_ = re.compile(r'\d+?/\d+')
            re_ = re.compile(r'\[\d+P\]')
            _name = re_.findall(txt)
            if _name:
                _num = int(_name[0][1:-1].upper().replace('P', ''))
                return txt[:-len(_name[0])], _num

        hdr = doc.header
        txt = hdr.h1.text
        title, total = ab(txt)
        # print(pic)
        # return pic
        # txt = txt.split('[')
        # title = txt[0]
        # print(title)
        # print(txt)
        # total = int(pic[1].upper().replace('P', ''))
        return title, total

    def analy_page_image_links(self, doc):
        imgs = []
        if not doc:
            log.warn('no content found')
            return imgs

        article = doc.article
        for art in article.find_all('p'):
            try:
                imgs.append(art.img.get('src'))
            except AttributeError as _:
                pass

        return imgs

    def fetch_page_image_links(self, page_url):
        imgs = []
        page_raw = self.bs4get(page_url)
        if not page_raw:
            log.error('cannot download from `{}`'.format(page_url))
            return imgs

        content = page_raw.find('div', 'content')
        imgs = self.analy_page_image_links(content)
        return imgs

    def fetch_all_links_by_url(self, page_info):
        if not isinstance(page_info, dict):
            page_info = {
                'name': '/'.join(page_info.split('/')[:-1])[1:],
                'page_url': page_info
            }

        title, imgs = self.get_all_imgs(urljoin(M['index'], page_info['page_url']))
        return os.path.join(page_info['name'], title), imgs

    def download_by_url(self, page_info):
        fd_abs = os.path.join(self.base_dir, page_info['fd'])
        if not os.path.exists(fd_abs):
            os.makedirs(fd_abs)
        os.chdir(fd_abs)

        params = [
            {
                'img_url': img_url,
                'title': '{}'.format(img_url.split('/')[-1])
            }
            for img_url in page_info['img_urls']
            ]

        _fail_count = 0
        for para in tqdm(params, ascii=True, desc='TEST'):
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
                log.warn('fail@5 img of this, skip({}) => ({})'.format(para['img_url'], 'TEST'))
                break

    def search_and_download(self, name):
        params = self.search_local(name)
        if not params:
            params = self.search_online(name)
        if not params:
            log.error('cannot find [{}]'.format(name.encode()))

        pool = Pool(processes=4)
        pool.map(self.download_by_url, params)
        pool.close()
        pool.join()

    def search_local(self, name):
        if not self.store:
            self.load_store()

        return self.store.get(name)

    def search_online(self, name):
        raw = self.bs4post(M['search'], urlencode({
            'keyword': name.encode('gbk'),
            's': '3944734779046070832'
        }))
        articles = raw.find_all('article', 'excerpt excerpt-one')
        links = []
        for art in articles:
            _ = art.header.h2.a.get('href')
            links.append(_)
            # if _:
            #     links.append(urljoin(M['index'], _))

        pages = [
            {
                'name': name,
                'page_url': link,
            }
            for link in links
            ]

        print(pages)
        pool = Pool(processes=4)

        results = []
        for page in pages:
            results.append(pool.apply_async(self.fetch_all_links_by_url, (page,)))

        pool.close()
        pool.join()

        info = []
        for rs in results:
            _fd, imgs = rs.get()
            info.append({
                'fd': _fd,
                'img_urls': imgs
            })

        if info:
            self.update_store(name, info)

        return info


@click.command()
@click.option('--name', '-n',
              help='the name of artist\nUSAGE: <cmd> -n <name>')
@click.option('--base_dir', '-d',
              help='the dir to store images\nUSAGE: <cmd> -d <dir_pth>')
def run(name, base_dir):
    if base_dir:
        abc.update_cfg('pjw.base_dir', base_dir)
    else:
        base_dir = cfg.get('pjw.base_dir')

    pj = Pjw(base_dir=base_dir)
    pj.search_and_download(name)


if __name__ == '__main__':
    run()
