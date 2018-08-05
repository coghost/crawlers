# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '2018/7/4 5:17 PM'
__description__ = '''
http://s.music.163.com/search/get/?type=1&limit=2&offset=0&s=``
'''

import os
import sys
import time

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

import requests

from izen import helper, dec
from logzero import logger as log
from multiprocessing import Pool, cpu_count
from multiprocessing.dummy import Pool as ThreadPool


class NetUri(object):
    search: str = 'http://s.music.163.com/search/get/'
    pic: str = 'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1530797339519&di=2cf33f5c6af926848ae5d30a20de0547&imgtype=0&src=http%3A%2F%2Fupload.chinaz.com%2F2017%2F1211%2F201712111701285331.jpg'
    csdn: str = 'https://blog.csdn.net/u010161379/article/details/51645264'


# net_ = {}


class GenHeader(object):
    def __init__(self, fpth='headers.txt', source='firefox'):
        self.fpth = fpth
        self.url = ''
        self.cookies = {}
        self.headers = {}
        getattr(self, 'parse_{}'.format(source))()

    def parse_firefox(self):
        """
        analy plain info from packet

        :return: (url, dat)
        :rtype:
        """
        packet = helper.read_file(self.fpth, False)
        dat = {}

        pks = [x for x in packet.split('\n') if x]

        for i, cnt in enumerate(pks[0:]):
            arr = cnt.split(': ')
            if len(arr) < 2:
                continue

            _k, v = arr[0], ':'.join(arr[1:])
            dat[_k] = v

        self.fmt_cookies(dat.pop('Cookie'))
        self.headers = dat

    def fmt_cookies(self, ck):
        """
        :param ck:
        :type ck:
        :return:
        :rtype:
        """
        cks = {}
        for c in ck.split(';'):
            a = c.split('=')
            if len(a) != 2:
                continue
            cks[a[0].replace(' ', '')] = a[1].replace(' ', '')
        self.cookies = cks


class ICrawl(object):
    def __init__(self, cookie_pth='netease.txt'):
        self.sess = requests.session()
        self.cookie_pth = cookie_pth
        self.req = GenHeader(self.cookie_pth)

    def get(self, url='', params=None, t='code'):
        log.debug('Start@ {}'.format(time.time()))
        if not url:
            if not params:
                return 0
            url = params.pop('url')
        rs = self.sess.get(url, headers=self.req.headers, params=params)
        # print('{} Got: [{}]'.format(rs.url, rs.status_code))
        if rs.status_code == 200:
            if t != 'code':
                return rs.json()
        log.debug('End with ({}) @ {}'.format(rs.status_code, time.time()))
        return rs.status_code


def n_get(params):
    # print(params.get('offset'))
    net_obj.get(params=params)


@dec.prt(1)
def r_1b1(crw):
    paras = [{
        'url': NetUri.pic,
        'limit': 100,
        'offset': _ * 100,
        'type': 1,
        's': '羽泉',
    } for _ in range(20)]

    # pool = Pool(processes=cpu_count())
    pool = Pool(8)
    # pool = ThreadPool(8)
    pool.map(n_get, paras)


def r_101(crw):
    urls = [NetUri.csdn for x in range(20)]
    # for _, url in enumerate(urls):
    #     c = crw.get(url)
    #     log.debug('Got {}: {}'.format(_, c))


def m9():
    # for i in range(1, 10):
    #     for j in range(1, i + 1):
    #         print('{}*{}={}'.format(j, i, j * i), end=' ')
    #     print()
    m = ['{}*{}={}'.format(j, i, j * i) for i in range(1, 10) for j in range(1, i + 1)]
    m = ['{}*{}={}{}'.format(j, i, j * i, '\r\n' if j == i else ' ') for i in range(1, 10) for j in
         range(1, i + 1)]
    print(''.join(m))
    print('\n'.join([' '.join(['%s*%s=%-2s' % (y, x, x * y) for y in range(1, x + 1)]) for x in range(1, 10)]))


def run():
    pass
    m9()
    # n = ICrawl(cookie_pth='csdn.txt')
    # r_1b1(n)
    # print(cpu_count())
    # r_101(n)


if __name__ == '__main__':
    # net_obj = ICrawl(cookie_pth='baiimg.txt')
    run()
