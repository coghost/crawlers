# -*- coding: utf-8 -*-
__date__ = '02/12 22:54'
__description__ = '''
'''

import os
import sys
import time
from pathlib import Path
from multiprocessing import Pool
import json
import math

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

import requests
from logzero import logger as zlog
from ihelp import helper
from iparse import IParser
import click

R = '\x1b[0;91m{}\x1b[0m'  # red
G = '\x1b[0;92m{}\x1b[0m'  # green
Y = '\x1b[0;93m{}\x1b[0m'  # yellow
SAVE_DIR = Path(os.path.expanduser('~/tmp/.nvs/'))
HOME_DIR = Path(app_root) / 'nvs'


class GirlStorage(object):
    def __init__(self, girl_id):
        self._file = str(SAVE_DIR / 'logs/girls.txt')
        self.girl_id = girl_id
        self.girls = {}
        self.spawn()

    def spawn(self):
        if helper.is_file_ok(self._file):
            self.girls = json.loads(helper.read_file(self._file, use_str=True))

    def _reshape(self):
        dat = {}
        for k, girl in self.girls.items():
            # finished:
            if girl.get('status', 0) == 0:
                girl['crawled'] = []
                dat[k] = girl
                continue

            if girl['pages'] in [0, 1]:
                girl['crawled'] = [girl['pages']]
                dat[k] = girl
                continue

            girl['crawled'] = [1]
            dat[k] = girl
        # self.girls = dat
        # self.sync()

    def filter_girls(self):
        finished = {}
        stored = {}
        for k, girl in self.girls.items():
            crawled = girl.get('crawled', [])
            pages = girl.get('pages', 0)
            status = len(crawled) >= pages
            if status:
                finished[k] = girl
            else:
                stored[k] = girl

        zlog.debug('found D/N/T: [{}/{}/{}] girls'.format(len(finished), len(stored), len(self.girls)))
        return stored, finished

    def prt(self, showed):
        info = []
        for k, girl in showed.items():
            crawled = girl.get('crawled', [])
            pages = girl.get('pages', 0)
            status = len(crawled) >= pages
            sym = G.format('✔') if status else Y.format('✘')

            info.append('{} {}/{}/[{}]\t{}'.format(
                sym, pages, k,
                ','.join([str(x) for x in crawled]),
                girl.get('name')
            ))
        info = sorted(info)
        print('\n'.join(info))

    def show(self, whom=None):
        stored, finished = self.filter_girls()
        if whom == 0:
            showed = stored
        elif whom == 1:
            showed = finished
        else:
            showed = self.girls

        self.prt(showed)

    def get_minimum_girl_id(self):
        stored, _ = self.filter_girls()

        info = [
            '{}/{}'.format(girl['pages'], k) for k, girl in stored.items()
        ]
        if info:
            info = sorted(info)
            d = info[0]
            d = d.split('/')[1].split('\t')[0]
            print(d, stored[d])
            return d
        else:
            zlog.warning('no more girls')
            sys.exit(0)

    def mark_done(self, page_num):
        # self.girls[self.girl_id].setdefault('status', {})
        _crawled = self.girls[self.girl_id].setdefault('crawled', [])
        _crawled.append(int(page_num))
        _crawled = sorted(list(set(_crawled)))
        self.girls[self.girl_id]['crawled'] = _crawled
        self.sync()

    def add(self, dat):
        name = dat.get('name')
        pages = dat.get('count') or 0
        pages = math.ceil(int(pages) / 30)
        print(pages)
        self.girls[self.girl_id] = {
            'name': name,
            'pages': pages,
        }
        self.sync()

    def delete(self):
        self.girls.pop(self.girl_id)
        self.sync()

    def sync(self):
        helper.write_file(json.dumps(self.girls), self._file)


class GirlParser(IParser):
    def __init__(self, raw_data='', file_name='', is_test_mode=True, **kwargs):
        kwargs['startup_dir'] = kwargs.get('startup_dir', HOME_DIR)
        if raw_data:
            kwargs['raw_data'] = raw_data
        file_name = SAVE_DIR / file_name
        super().__init__(file_name, is_test_mode=is_test_mode, **kwargs)


class GirlHomeParser(GirlParser):
    pass


class GirlAlbumPageParser(GirlParser):
    pass


class GirlAlbumParser(GirlParser):
    pass


class GirlCrawler(object):
    def __init__(self, girl_id, header_file='/tmp/nvs.txt'):
        self.sess = requests.session()
        self.cookies = {}
        self.headers = {}
        self.girl_id = str(girl_id)
        self.base_dir = SAVE_DIR
        self.store = GirlStorage(self.girl_id)
        self.saved = 0

        self.parse_headers(header_file)

    def parse_headers(self, header_file):
        """
        analyze headers from file
        """
        packet = helper.to_str(helper.read_file(header_file))
        dat = {}

        pks = [x for x in packet.split('\n') if x.replace(' ', '')]

        for i, cnt in enumerate(pks[1:]):
            arr = cnt.split(':')
            if len(arr) < 2:
                continue
            arr = [x.replace(' ', '') for x in arr]
            _k, v = arr[0], ':'.join(arr[1:])
            dat[_k] = v

        self.fmt_cookies(dat.pop('Cookie', ''))
        self.headers = dat

    def fmt_cookies(self, raw_cookie):
        if not raw_cookie:
            return
        cks = {}
        for c in raw_cookie.split(';'):
            a = c.split('=')
            if len(a) != 2:
                continue
            cks[a[0].replace(' ', '')] = a[1].replace(' ', '')
        self.cookies = cks

    def parallel_download(self, urls, procs=16):
        self.total_jobs = len(urls)
        result = []
        pool = Pool(processes=procs)
        for p in urls:
            result.append(pool.apply_async(self.get_img, (p,)))
        pool.close()
        pool.join()

        dat = []
        e404 = []
        ok = 0
        for res in result:
            code, d = res.get()
            if not code:
                continue
            if code == 404:
                e404.append(d)
            elif code == 3:
                dat.append(d)
            else:
                ok += 1

        zlog.warning('404/failed/valid: {}/{}/{}'.format(len(e404), R.format(len(dat)), ok))
        return e404, ok

    def do_get(self, url, save_to):
        if helper.is_file_ok(save_to):
            return 200
        res = self.sess.get(url, headers=self.headers, cookies=self.cookies, timeout=30)
        if res.status_code == 404:
            zlog.error('[{}]: {}'.format(res.status_code, url))
            return 404
        helper.write_file(res.content, save_to)
        zlog.debug('[{}] saved {}'.format(res.status_code, url))
        return res.status_code

    @staticmethod
    def concat_album_images(album_id, total):
        urls = []
        url = 'https://img.onvshen.com:85/gallery/' + album_id + '/{}.jpg'
        urls.append(url.format('0'))
        for i in range(1, total):
            if i < 10:
                p = '00{}'.format(i)
            elif i < 100:
                p = '0{}'.format(i)
            else:
                p = '{}'.format(i)

            urls.append(url.format(p))
        return urls

    def gen_pth_by_url(self, url):
        name = url.split('/')[-1]
        fd = '/'.join(url.split('/')[-3:-1])
        name = f"{fd.replace('/', '_')}_{name}"
        img_pth = self.base_dir / '{0}/{1}'.format(fd, name)
        if helper.is_file_ok(img_pth):
            return ''
        return img_pth

    def get_img(self, url):
        try:
            img_pth = self.gen_pth_by_url(url)
            if img_pth:
                code = self.do_get(url, img_pth)
                time.sleep(0.1)
                return code, url
            return 0, ''
        except Exception as e:
            zlog.error('failed: {}'.format(url))
            return 3, url

    def get_album_pages(self, index=1):
        save_to = self.base_dir / self.girl_id / 'album_page/{}.html'.format(index)
        if index:
            url = 'https://www.nvshens.net/girl/{}/album/{}.html'.format(self.girl_id, index)
        else:
            url = 'https://www.nvshens.net/girl/{}'.format(self.girl_id)
        zlog.debug('get album: {}'.format(url))
        self.do_get(url, save_to)

    def get_album(self, album_id):
        url = 'https://www.nvshens.net/g/{}/'.format(album_id)
        save_to = self.base_dir / self.girl_id / 'albums/{}.html'.format(album_id)
        self.do_get(url, save_to)

    def get_single_album_images(self, album_id):
        self.get_album(album_id)
        ga = GirlAlbumParser(file_name='{}/albums/{}.html'.format(self.girl_id, album_id))
        ga.do_parse()
        count = ga.data.get('count')
        images = self.concat_album_images('{}/{}'.format(self.girl_id, album_id), count)
        return images

    def get_album_images(self, index=1):
        self.get_album_pages(index)
        gap = GirlAlbumPageParser(file_name='{}/album_page/{}.html'.format(self.girl_id, index))
        gap.do_parse()

        albums = gap.data.get('albums')
        albums = [
            x.split('/')[-2] for x in albums
        ]
        zlog.debug('{} => {}/{}\n{}'.format(self.girl_id, index, len(albums), albums))
        avail_images = []
        for album in albums:
            avail_images += self.get_single_album_images(album)

        helper.write_file('\n'.join(avail_images), self.base_dir / 'logs/{}-{}.txt'.format(self.girl_id, index))

    def get_all_albums(self):
        url = 'https://www.nvshens.net/girl/{}/'.format(self.girl_id)
        save_to = self.base_dir / self.girl_id / 'albums/home.html'
        self.do_get(url, save_to=save_to)
        ghp = GirlHomeParser(file_name='{}/albums/home.html'.format(self.girl_id))
        ghp.do_parse()
        dat = ghp.data
        self.store.add(dat)
        girl = self.store.girls.get(self.girl_id)
        zlog.debug('found: {}'.format(girl))
        start_page = 1
        if not girl['pages']:
            start_page = 0

        for page in range(start_page, girl['pages'] + 1):
            zlog.debug('get page {}'.format(page))
            self.get_album_images(index=page)


@click.command(
    context_settings=dict(
        help_option_names=['-h', '--help'],
        terminal_width=200,
    ),
)
@click.option('--girl_id', '-id', default='0')
@click.option('--album_id', '-ad')
@click.option('--auto_mode', '-a', is_flag=True)
@click.option('--page_num', '-n', default='1')
@click.option('--generate_album_images', '-ab', is_flag=True)
@click.option('--process', '-p', default=16, type=int)
@click.option('--force', '-f', is_flag=True, help='force skip 404 files')
@click.option('--view', '-v', is_flag=True)
@click.option('--whom', '-w', type=int)
@click.option('--delete_girl', '-d', is_flag=True)
def run(girl_id, page_num, generate_album_images, process, force, view, whom, delete_girl, album_id, auto_mode):
    gc = GirlCrawler(girl_id, header_file=str(SAVE_DIR / 'header.txt'))
    if view or whom is not None:
        gc.store.show(whom)
        return
    if delete_girl:
        gc.store.delete()
        return

    if auto_mode:
        girl_id = gc.store.get_minimum_girl_id()
        zlog.debug('start with girl-id: {}'.format(girl_id))

    if generate_album_images:
        gc.get_all_albums()
        return

    if album_id:
        images = gc.get_single_album_images(album_id)
        helper.write_file('\n'.join(images), gc.base_dir / 'logs/{}-{}.txt'.format(girl_id, album_id))

    girl_info = gc.store.girls.get(girl_id, {})
    if not girl_info.get('pages', 0):
        page_num = 0

    if album_id:
        page_num = album_id

    img_file = str(SAVE_DIR / 'logs/{}-{}.txt'.format(girl_id, page_num))
    e404_file = str(SAVE_DIR / 'logs/{}-{}-404.txt'.format(girl_id, page_num))
    # print(img_file, e404_file)

    e404 = []
    if not force and helper.is_file_ok(e404_file):
        e404 = [x for x in helper.read_file(e404_file, use_str=True).split('\n') if x]

    images = [x for x in helper.read_file(img_file, use_str=True).split('\n') if x]
    # gc = GirlCrawler(girl_id)
    todo = []
    for img in images:
        d = gc.gen_pth_by_url(img)
        if img in e404:
            continue
        if d:
            todo.append(str(img))

    zlog.debug('all/todo/404: {}/{}/{}'.format(len(images), len(todo), len(e404)))
    if not todo:
        zlog.info('all image of {} downloaded'.format(girl_id))
        gc.store.mark_done(page_num)
        return

    e404_, ok = gc.parallel_download(urls=todo, procs=process)
    if e404_:
        e404 += e404_
        helper.write_file('\n'.join(sorted(e404)), e404_file)
    else:
        if ok == len(todo):
            zlog.info('all image of {} downloaded'.format(girl_id))
            gc.store.mark_done(page_num)


if __name__ == '__main__':
    run()
