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
from http import cookiejar

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from bs4 import BeautifulSoup as BS
from logzero import logger as log

# from base import abc
from izen import helper


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
        """
            使用 bs4 来格式化 markup 文本

        :param markup: ``html文本``
        :type markup: str
        :param parser: ``解析使用库``
        :type parser: str
        :param encoding: ``编码类型``
        :type encoding: str
        :return: BeautifulSoup
        """
        _ec = encoding if encoding else self.encoding
        _ps = parser if parser else self.parser
        if not encoding:
            return BS(markup, _ps)
        return BS(markup, _ps, from_encoding=_ec)

    def bs4post(self, req_params, retry=1, use_redirect_location=False):
        while retry > 0:
            res = self.do_post(req_params, use_redirect_location)
            if res and use_redirect_location:
                return res
            if res:
                return BS(res, self.parser, from_encoding=self.encoding)
            retry -= 1

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

    def do_get(self, params, is_json=False, show_log=False):
        """ 简单封装 requests get

        :param params: requests 支持的参数
        :type params:
        :param is_json: 参数是否是 json 格式
        :type is_json:
        :param show_log: 是否展示请求的 url
        :type show_log: bool
        :return:
        """
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
            if show_log:
                log.debug(res.url)
            if res:
                if is_json:
                    content = res.json()
                else:
                    content = res.content
        except (requests.ReadTimeout, requests.ConnectTimeout, requests.ConnectionError) as _:
            pass
        finally:
            if content:
                return content
            else:
                log.error('{} cannot reached'.format(params.get('url')))

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
                    content += helper.to_str(dat)
                return content

            with click.progressbar(length=content_size, label='fetch') as bar:
                for dat in res.iter_content(chunk_size=chunk_size, decode_unicode=True):
                    content += helper.to_str(dat)
                    bar.update(chunk_size)
            return content

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
                    content += helper.to_str(dat)
                return content

            with click.progressbar(length=content_size, label='fetch') as bar:
                for dat in res.iter_content(chunk_size=chunk_size, decode_unicode=True):
                    content += helper.to_str(dat)
                    bar.update(chunk_size)
            return content

    @staticmethod
    def dump_cookies(cookies):
        _cookie_jar = cookiejar.LWPCookieJar('cookie.txt')
        requests.utils.cookiejar_from_dict({
            c.name: c.value
            for c in cookies
        }, _cookie_jar)
        _cookie_jar.save('cookie.txt', ignore_discard=True, ignore_expires=True)

    @staticmethod
    def load_cookies():
        if not helper.is_file_ok('cookie.txt'):
            return
        _cookie_jar = cookiejar.LWPCookieJar('cookie.txt')
        _cookie_jar.load('cookie.txt', ignore_expires=True, ignore_discard=True)
        _cookies = requests.utils.dict_from_cookiejar(_cookie_jar)
        cookies = requests.utils.cookiejar_from_dict(_cookies)
        return cookies

    @staticmethod
    def clear_empty_img(dir_pth, do_clear=False):
        helper.clear_empty_file(dir_pth, ['jpg'], do_clear)

    def download_and_save(self, params, force_write=False):
        img_url, title = params.get('img_url'), params.get('title')

        if not force_write and helper.is_file_ok(title):
            return self.save_status['skip']

        img = self.crawl(img_url)
        if not img:
            return self.save_status['fail']
        with open(title, 'wb') as f:
            f.write(img)
        return self.save_status['ok']

    def use_proxy(self):
        proxies = [
            '117.90.108.101:49651',
            '113.121.168.35:27287',
            '113.93.103.89:28221',
            '49.87.75.51:35257',
            '121.205.254.227:49435',
            '115.204.34.176:35862',
            '60.175.199.109:23760',
            '171.14.208.81:33804',
            '222.95.37.81:34422',
            '49.87.182.181:36147',
        ]
        # proxy_ = {
        #     'https': proxies[0],
        # 'https': '61.155.164.112:3128',
        # }
        # print(proxy_)
        # uri = 'https://httpbin.org/get'
        # uri = 'http://2017.ip138.com/ic.asp'
        # uri = 'https://www.youtube.com'
        # uri = 'https://twitter.com/'
        # uri = 'https://www.baidu.com/'
        uri = 'http://www.xicidaili.com/nn'
        # uri = 'http://proxydb.net/?country=JP&offset=90'
        for p in proxies:
            try:
                print(p, end=', ')
                rs = requests.get(
                    uri,
                    proxies={
                        'http': p,
                    },
                    timeout=10)
                # rs = requests.get(uri)
                print(rs.status_code)
                # print(rs.text)
            except Exception as _:
                print()
                pass


if __name__ == '__main__':
    # log.debug('crawler base.')
    c = Crawl()
    c.use_proxy()
