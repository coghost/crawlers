# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '26/10/2017 10:17 AM'
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
from urllib.parse import urlencode
import re

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from bs4 import BeautifulSoup as BS
from logzero import logger as log

# https://github.com/chenjiandongx/awesome-spider
from base import abc


class Crawl(object):
    def __init__(self, refer='', parser='lxml', encoding='utf-8'):
        # 'content-encoding': 'gzip',
        self.headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/61.0.3163.100 '
                          'Safari/537.36',
        }
        self.post_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/61.0.3163.100 '
                          'Safari/537.36',
        }
        self.save_status = {
            'skip': 0,
            'fail': 1,
            'ok': 3,
        }
        if parser:
            self.parser = parser
        if refer:
            self.headers['Referer'] = refer
        self.encoding = encoding

    def bs4post(self, url, payload, to=5, retry=0):
        res = self.do_post(url, payload, to, retry)
        if res:
            return BS(res, self.parser, from_encoding=self.encoding)

    def bs4get(self, url, to=5, retry=0, parser=''):
        """
            返回经 ``bs4`` 格式化后的文档

        :param parser:
        :type parser:
        :param url:
        :type url:
        :param to:
        :type to:
        :param retry:
        :type retry:
        :return:
        :rtype:
        """
        res = self.crawl(url, to, retry)
        if not parser:
            parser = self.parser
        if res:
            return BS(res, parser, from_encoding=self.encoding)

    def do_post(self, url, payload, to=5, retry=0, use_json=False):
        """
        使用 ``request.get`` 从指定 url 获取数据

        :param use_json: 是否使用 ``json`` 格式, 如果是, 则可以直接使用字典, 否则需要先转换成字符串
        :type use_json: bool
        :param payload: 实际数据内容
        :type payload: dict
        :param url: ``接口地址``
        :type url:
        :param to: ``响应超时返回时间``
        :type to:
        :return: ``接口返回的数据``
        :rtype: dict
        """
        para = {
            'url': url,
            'data': payload,
            'timeout': to,
            'headers': self.post_headers,
        }
        if use_json:
            para.pop('data')
            para['json'] = payload

        rs = requests.post(**para)
        if rs.status_code == 200:
            return rs.content

    def crawl(self, url, to=5, retry=0):
        i = 0
        content = None
        while i <= retry:
            i += 1
            try:
                res = requests.get(url, headers=self.headers, timeout=to)
                if res:
                    content = res.content
            except (requests.ReadTimeout, requests.ConnectTimeout, requests.ConnectionError) as _:
                pass
            finally:
                if content:
                    return content
                else:
                    log.error('{} cannot reached'.format(url))

    @staticmethod
    def clear_empty_img(dir_pth, do_clear=False):
        abc.clear_empty_file(dir_pth, ['jpg'], do_clear)

    def download_and_save(self, params, force_write=False):
        img_url, title = params.get('img_url'), params.get('title')

        if not force_write and abc.is_file_ok(title):
            return self.save_status['skip']

        img = self.crawl(img_url)
        if not img:
            return self.save_status['fail']
        with open(title, 'wb') as f:
            f.write(img)
        return self.save_status['ok']


if __name__ == '__main__':
    log.debug('crawler base.')
