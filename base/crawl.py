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
import click
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

    def bs4markup(self, markup, parser='', encoding=''):
        _ec = encoding if encoding else self.encoding
        _ps = parser if parser else self.parser
        return BS(markup, _ps, from_encoding=encoding)

    def bs4post(self, req_params, retry=1, use_redirect_location=False):
        while retry > 0:
            res = self.do_post(req_params, use_redirect_location)
            if res and use_redirect_location:
                return res
            if res:
                return BS(res, self.parser, from_encoding=self.encoding)
            retry -= 1

    # @abc.bs4markup()
    def do_post(self, req_params, use_redirect_location=False):
        """
            使用 ``request.post`` 从指定 url 获取数据,

        - 如果获取结果是 html, 则使用 ``BeautifulSoup`` 封装
        - 如果非 html 标识, 则直接返回结果

        :return: ``接口返回的数据``
        """
        if isinstance(req_params, str):
            req_params = {'url': req_params}
        if req_params.get('headers'):
            h = req_params.pop('headers')
            self.post_headers = dict(self.post_headers, **h)

        para = {
            'timeout': req_params.get('timeout', 5),
            'headers': self.post_headers,
        }

        # 使用 para 的值, 更新覆盖 req_params 的值
        para = dict(req_params, **para)
        rs = requests.post(**para)

        if use_redirect_location:
            return rs.headers.get('location', '')

        if rs.status_code == 200:
            return rs.content

    def bs4get(self, url, to=5, retry=0, parser='', headers=None):
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
        res = self.crawl(url, to, retry, headers=headers)
        if not parser:
            parser = self.parser
        if res:
            return BS(res, parser, from_encoding=self.encoding)

    def crawl(self, url, to=5, retry=0, headers=None):
        i = 0
        if headers:
            self.headers = dict(self.headers, **headers)
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

    def do_get(self, params):
        if isinstance(params, str):
            params = {'url': params}
        if params.get('headers'):
            h = params.pop('headers')
            self.headers = dict(self.headers, **h)

        para = {
            'timeout': params.get('timeout', 5),
            'headers': self.headers,
            'stream': True,
        }
        # 使用 para 的值, 更新覆盖 req_params 的值
        para = dict(params, **para)
        content = ''
        try:
            res = requests.get(**para)
            if res:
                content = res.content
        except (requests.ReadTimeout, requests.ConnectTimeout, requests.ConnectionError) as _:
            pass
        finally:
            if content:
                return content
            else:
                log.error('{} cannot reached'.format(params.get('url')))

    # @abc.bs4markup()
    def stream_post(self, params, use_redirect_location=False, chunk_size=1024, show_bar=False):
        if isinstance(params, str):
            params = {'url': params}
        if params.get('headers'):
            h = params.pop('headers')
            self.post_headers = dict(self.post_headers, **h)

        para = {
            'timeout': params.get('timeout', 5),
            'headers': self.post_headers,
            'stream': True,
        }
        # 使用 para 的值, 更新覆盖 req_params 的值
        para = dict(params, **para)

        content = ''
        with requests.post(**para) as res:
            if use_redirect_location:
                return res.headers.get('location', '')

            if 'content-length' not in res.headers:
                return res.content

            content_size = int(res.headers['content-length'])  # 内容体总大小
            if not show_bar:
                for dat in res.iter_content(chunk_size=chunk_size, decode_unicode=True):
                    content += abc.to_str(dat)
                return content

            with click.progressbar(length=content_size, label='fetch') as bar:
                for dat in res.iter_content(chunk_size=chunk_size, decode_unicode=True):
                    content += abc.to_str(dat)
                    bar.update(chunk_size)
            return content

    # @abc.bs4markup()
    def stream_get(self, params, chunk_size=1024, show_bar=True, encoding=''):
        if isinstance(params, str):
            params = {'url': params}

        if params.get('headers'):
            h = params.pop('headers')
            self.headers = dict(self.headers, **h)

        para = {
            'timeout': params.get('timeout', 5),
            'headers': self.headers,
            'stream': True,
        }
        # 使用 para 的值, 更新覆盖 req_params 的值
        para = dict(params, **para)

        content = ''
        # _encoding = encoding
        with requests.get(**para) as res:
            _encoding = res.encoding
            if 'content-length' not in res.headers:
                return res.content

            content_size = int(res.headers['content-length'])  # 内容体总大小
            # print(res.encoding)

            if not show_bar:
                for dat in res.iter_content(chunk_size=chunk_size, decode_unicode=True):
                    content += abc.to_str(dat)
                return content

            with click.progressbar(length=content_size, label='fetch') as bar:
                for dat in res.iter_content(chunk_size=chunk_size, decode_unicode=True):
                    content += abc.to_str(dat)
                    bar.update(chunk_size)
            return content

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
