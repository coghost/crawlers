# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '05/12/2017 2:21 PM'
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
from urllib.parse import urljoin, urlencode

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import click
from logzero import logger as log
from izen import helper
from base import abc
from base.phant import PhantomPy

M = {
    'index': 'http://proxydb.net/',
    'refer': 'http://proxydb.net/',
}
catch_error = False


class ProxyDB(PhantomPy):
    def __init__(self):
        PhantomPy.__init__(self)

    @abc.bs4markup({'parser': 'html5lib'})
    def ph_fetch(self, params):
        _par = urlencode(params)
        url = '{}?{}'.format(M['index'], _par)
        log.debug('url: ({})'.format(url))
        return self.do_get(url)

    @helper.catch(catch_error, AttributeError)
    def take_proxies(self, table_raw):
        """
            解析 table, 并以表头为key 生成对应的字典结构

        :param table_raw:
        :return:
        """
        dat = []
        keys = []

        # gen keys
        try:
            for th in table_raw.thead.tr.find_all('th'):
                k = th.text.split(' ')
                k = k[-1].lower()
                keys.append(k)

            def td_line_to_proxy(doc_tr):
                d = {}
                tds = doc_tr.find_all('td')

                d[keys[0]] = tds[0].find('a').text
                for i, td in enumerate(tds[1:], start=1):
                    d[keys[i]] = td.text.replace('\n', '').replace(' ', '')
                dat.append(d)

            for tr in table_raw.tbody.find_all('tr'):
                td_line_to_proxy(tr)

            return dat
        except AttributeError as _:
            log.error('{}'.format(table_raw))

    def fetch_one_page(self, params):
        raw = self.ph_fetch(params)
        if not raw:
            log.error('Nothing')
            return

        table = raw.find('table')
        _proxies = self.take_proxies(table)
        return _proxies

    def fetch_all_page(self):
        pass


@click.command()
@click.option('--country', '-c',
              default='CN',
              help='find by country name\nUSAGE: <cmd> -c <country>')
@click.option('--protocol', '-t',
              help='find by protocol name\nUSAGE: <cmd> -t <p1,...>')
@click.option('--min_uptime', '-u',
              type=int,
              default=75,
              help='the min uptime\nUSAGE: <cmd> -u <num>')
@click.option('--max_response_time', '-r',
              type=int,
              default=5,
              help='the max response time\nUSAGE: <cmd> -r <num>')
@click.option('--page', '-p',
              type=int,
              default=0,
              help='the page to fetch\nUSAGE: <cmd> -p <num>')
def run(country, protocol, min_uptime, max_response_time, page):
    if protocol == 'all':
        protocol = ''
    params = {
        'country': country,
        'min_uptime': min_uptime,
        'max_response_time': max_response_time,
        'offset': page * 15,  # current page size
    }
    if protocol:
        params['protocol'] = protocol.split(',')

    p = ProxyDB()
    if page >= 0:
        _proxies = p.fetch_one_page(params)
        _ = json.dumps(_proxies)
        helper.copy_to_clipboard(_)
        print(_)
    else:
        p.fetch_all_page()


if __name__ == '__main__':
    run()
