import os
import sys
from pathlib import Path

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

import click
from icraw import AsyncCrawler
from iparse import IParser
from ihelp import helper
from logzero import logger as zlog

SAVE_DIR = Path(os.path.expanduser('~/Pictures/win4k/'))
HOME_DIR = Path(app_root) / 'win4k'


def R(raw_string):
    return '\x1b[0;91m{}\x1b[0m'.format(raw_string)


def G(raw_string):
    return '\x1b[0;92m{}\x1b[0m'.format(raw_string)


def Y(raw_string):
    return '\x1b[0;93m{}\x1b[0m'.format(raw_string)


class GirlParser(IParser):
    def __init__(self, raw_data='', file_name='', is_test_mode=True, **kwargs):
        kwargs['startup_dir'] = kwargs.get('startup_dir', HOME_DIR)
        if raw_data:
            kwargs['raw_data'] = raw_data
        super().__init__(file_name, is_test_mode=is_test_mode, **kwargs)


class AlbumParser(GirlParser):
    pass


class Win4k(AsyncCrawler):
    def __init__(self, **kwargs):
        self.save_to = SAVE_DIR
        self.size = ''
        self.min_size = kwargs.pop('min_size', 0)
        self._config_startup(kwargs.pop('size', ''))
        self.downloaded = []
        super().__init__(**kwargs)

    def _config_startup(self, size):
        if size:
            self.size = set([int(x) for x in size.split(',')])
        self.go_through()

    def go_through(self):
        all_dirs = []
        for root_, dirs, files in os.walk(self.save_to):
            if root_ == str(self.save_to):
                continue
            if dirs:
                all_dirs += dirs

        self.downloaded = all_dirs

    def get_4k_page(self, page_id, abs_url=False, test_keys=None):
        if not abs_url:
            url = '{}/{}.html'.format(self.homepage, page_id)
        else:
            url = page_id

        raw = self.load(url)
        kwargs = {}
        if test_keys:
            kwargs['test_keys'] = test_keys
        ap = AlbumParser(raw_data=raw, **kwargs)
        ap.do_parse()
        return ap.data

    def get_albums(self, page_id, abs_url=False):
        page_id = 'meinvtag{}'.format(page_id)
        dat = self.get_4k_page(page_id, abs_url, test_keys=['albums'])
        albums = dat.get('albums').get('albums')
        name = dat.get('albums').get('album_name').replace('图片大全', '')
        return name, albums

    def check_size(self, dat, page_id):
        size = set([int(x) for x in dat.get('size', '').split('*')])
        if self.size:
            _found = self.size and size
            if _found:
                zlog.info('matched: {}'.format(_found))
                return True
            else:
                zlog.debug('skipped: {}/{}'.format(self.size, size))
                return False

        _msg = '{} size is: {}'.format(page_id, Y(size))
        size = max(size)
        if self.min_size:
            if size < self.min_size:
                zlog.info('skip min_size: {}/{}'.format(_msg, self.min_size))
                return False
            else:
                zlog.info('crawl min_size: {}/{}'.format(_msg, self.min_size))
                return True

        if size <= 1920:
            ok = click.confirm(_msg, default=True)
            if not ok:
                zlog.info('skip too small image: {}'.format(page_id))
                return []
            else:
                return True
        else:
            zlog.info('start download {}'.format(_msg))
            return True

    def get_album_images(self, page_id, abs_url=False):
        if not abs_url:
            page_id = 'meinv{}'.format(page_id)
        dat = self.get_4k_page(page_id, abs_url, test_keys=['images'])
        dat = dat.get('images')
        size = self.check_size(dat, page_id)
        if not size:
            return []
        images = [
            '{}.jpg'.format(x.split('_')[0])
            for x in dat['url']
        ]

        return images

    def fetch_single_album_images(self, name, album_id, last_one=True):
        images = self.get_album_images(album_id)
        if not images:
            return
        zlog.debug('{}.{} total has {} images'.format(G(name), G(album_id), G(len(images))))
        _save_to = self.save_to / '{}/{}'.format(name, album_id)
        helper.mkdir_p(_save_to, is_dir=True)
        self.run(images, 4, preset_pth=_save_to, final_task=last_one)
        print('final result ok/fail/skip: {ok}/{fail}/{skip}'.format(**self.result))


@click.command(
    context_settings=dict(
        help_option_names=['-h', '--help'],
        terminal_width=200,
    ),
)
@click.option('--name', '-n', default='')
@click.option('--album_id', '-id')
@click.option('--tag_id', '-tid')
@click.option('--offset', '-o', default=0, type=int)
@click.option('--size_list', '-s')
@click.option('--min_size', '-min', type=int)
@click.option('--confirm', '-c', is_flag=True)
def run(name, album_id, tag_id, offset, size_list, min_size, confirm):
    wk = Win4k(site_init_url='http://www.win4000.com/', size=size_list, min_size=min_size)

    if album_id:
        name = name or 'one'
        album_id = album_id.split('_')[0].replace('meinv', '')
        wk.fetch_single_album_images(name, album_id)
        return

    if tag_id:
        tag_id = tag_id.replace('meinvtag', '')
        _name, albums = wk.get_albums(tag_id)
        name = name or _name
        zlog.info('start download: {}'.format(name))
        for i, album in enumerate(albums[offset:]):
            url = album['url']
            _name = album['name']
            album_id = url.split('/')[-1].split('.')[0].replace('meinv', '')
            _msg = 'try {}: {} / {}'.format(i + offset + 1, album_id, _name)

            if confirm and not click.confirm(_msg, default=False):
                continue

            zlog.info(_msg)
            wk.fetch_single_album_images(name, album_id, last_one=i + 1 == len(albums))


if __name__ == '__main__':
    run()
