# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '2018/6/13 3:58 PM'
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

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

from izen import helper


class MkHeader(object):
    def __init__(self, fpth='headers.txt'):
        self.fpth = fpth
        self.url = ''
        self.cookies = {}
        self.headers = {}
        self.parse_charles()

    def parse_charles(self):
        """
        analy plain info from charles packet

        :return: (url, dat)
        :rtype:
        """
        packet = helper.to_str(helper.read_file(self.fpth))
        dat = {}

        pks = [x for x in packet.split('\n') if x.replace(' ', '')]
        url = pks[0].split(' ')[1]

        for i, cnt in enumerate(pks[1:]):
            arr = cnt.split(':')
            if len(arr) < 2:
                continue
            arr = [x.replace(' ', '') for x in arr]
            _k, v = arr[0], ':'.join(arr[1:])
            dat[_k] = v

        self.fmt_cookies(dat.pop('Cookie'))
        self.headers = dat
        self.url = 'https://{}{}'.format(self.headers.get('Host'), url)
        # return url, dat

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


def run():
    mkh = MkHeader()
    # url, dat = mkh.parse_charles()

    # url, dat = parse_charles()
    print(mkh.url)
    for k, v in mkh.headers.items():
        print(k, v)

    for k, v in mkh.cookies.items():
        print(k, v)


if __name__ == '__main__':
    run()
