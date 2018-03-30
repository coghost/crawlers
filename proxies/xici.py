#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '06/12/2017 11:40 AM'
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
from multiprocessing import Pool, cpu_count

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import click
from logzero import logger as log
from tqdm import tqdm
from izen import helper
from base.crawl import Crawl
from base import abc
from base.abc import cfg
from proxies import mg_doc
from base import dbstore

M = {
    'index': 'http://www.xicidaili.com/nn/{}',
    'refer': 'http://www.xicidaili.com/nn',
}


class Xici(Crawl):
    def __init__(self,
                 refer=M.get('refer', ''),
                 parser='html5lib',
                 ):
        Crawl.__init__(self, refer,
                       parser=parser)
        self.end_date = ''

    def load_latest_record_date(self):
        p = mg_doc.Proxies.objects().order_by('-checked').first()
        if p:
            self.end_date = p.checked

    def get_page(self, page_index=1):
        url = M['index'].format(page_index)
        proxies = {'http': '218.17.30.29:8888'}
        _raw = self.do_get({
            'url': url,
            # 'proxies': proxies,
        })
        if not _raw:
            return
        raw = self.bs4markup(_raw)

        table = raw.find('table', id='ip_list')
        return self.take_proxies(table=table)

    @staticmethod
    def take_proxies(table):
        """ 解析 table 数据生成 dict 结构

        :param table:
        :return:
        """
        keys = 'country,ip,port,location,anonymity,protocol,speed,conn_time,alive,checked'.split(',')
        trs = table.find('tbody').find_all('tr')

        dat = []
        for tr in trs[1:]:
            try:
                d = {}
                tds = tr.find_all('td')
                c = tds[0]

                # column 1 is image, use alt attr
                country_name = '--'
                if c.find('img'):
                    country_name = c.img.get('alt')

                d[keys[0]] = country_name
                for i, td in enumerate(tds[1:], start=1):
                    txt = td.text.replace('\n', '').rstrip().lstrip()
                    if txt:
                        d[keys[i]] = txt
                        continue

                    # if no text, use title for instead
                    _txt = ''
                    if td.find('div', 'bar'):
                        _txt = td.find('div', 'bar').get('title')

                    d[keys[i]] = _txt

                dat.append(d)
            except AttributeError as _:
                log.debug('{}: {}'.format(tr, _))

        return dat

    def get_pages(self, end_date=''):
        """
            获取到 ``end_date`` 的所有可用 proxies

        :param end_date:
        :return:
        """
        dat = []
        page_index = 1
        self.end_date = end_date or cfg['xici.end_date']

        while True:
            dat += self.get_page(page_index)
            page_index += 1
            if dat[-1]['checked'] < self.end_date:
                abc.update_cfg('d4.base_dir', dat[0]['checked'])
                break
            time.sleep(1)

        return dat

    @staticmethod
    def save_to_db(dat):
        dbstore.batch_write(dat, 'xici.proxies')
        # for d in dat:
        #     xi_mg_doc.save_it(d)

    @staticmethod
    def search(location='', limit_num=10):
        if location:
            docs = mg_doc.Proxies.objects(location__icontains=location)[:limit_num]
        else:
            docs = mg_doc.Proxies.objects()[:limit_num]
        return docs

    def is_proxy_alive_byip138(self, dat):
        """
            使用 ip138 来测试代理是否成功.

        :param dat:
        :return:
        """
        _key = dat.protocol.lower()
        if _key == 'https':
            return
        url = 'http://2017.ip138.com/ic.asp'
        proxies = {_key: '{}:{}'.format(dat.ip, dat.port)}
        rs = self.do_get({
            'url': url,
            'proxies': proxies,
            'timeout': 10
        })
        if rs:
            print(self.bs4markup(rs, parser='lxml', encoding='gb2312').find('center').text)

    def crawl_all_page(self):
        """
            - 获取总页数
            - 启动多个进程爬取
            - 写入已完成的页数到 db
        :return:
        """

        def get_total_num():
            url = M['index'].format(1)
            raw = self.bs4markup(self.do_get(url))
            pagi = raw.find('div', 'pagination')
            return pagi.find_all('a')[-2]

        def crawl_each(idx):
            return self.get_page(idx)
            # print('CRAWL: {}'.format(idx))
            # return []

        def update_done_num(idx):
            """
                更新已完成数字到 ``redis`` 中

            :param idx:
            :return:
            """
            abc.update_cfg('xici.last_index', idx)
            # print('DONE: {}'.format(idx))
            # return idx

        # total = get_total_num()
        total = 2564
        st = 0
        each_size = 100

        # dat = []
        while True:
            start_str = 'START@{}'.format(st * each_size)
            for i in tqdm(range(st * each_size, (st + 1) * each_size), ascii=True, desc=start_str):
                if i <= int(cfg.get('xici.last_index', 0)):
                    continue

                if i > total:
                    return

                _ = crawl_each(i)
                if _:
                    self.save_to_db(_)
                    update_done_num(i)
                    a = abc.randint(6, 14)
                    time.sleep(a)
            st += 1


@click.command()
@click.option('--init', '-i',
              is_flag=True,
              help='init all pages\nUSAGE: <cmd> -i')
# @click.option('--update', '-u',
#               is_flag=True,
#               help='update local cache\nUSAGE: <cmd> -u')
@click.option('--details', '-d',
              is_flag=True,
              help='show detail info\nUSAGE: <cmd> -d')
@click.option('--is_alive', '-a',
              is_flag=True,
              help='test ip is alive or not\nUSAGE: <cmd> -a')
@click.option('--location', '-l',
              help='search by location\nUSAGE: <cmd> -l <location>')
@click.option('--nums', '-n',
              type=int,
              default=10,
              help='search by location\nUSAGE: <cmd> -l <location>')
def run(location, nums, is_alive, details, init):
    xc = Xici()
    if init:
        xc.crawl_all_page()
        return

    # if update:
    #     xc.load_latest_record_date()
    #     dat = xc.get_pages()
    #     xc.save_to_db(dat)
    #     return

    recs = xc.search(location, nums)
    for rec in recs:
        _op = '{:>6} → {}:{}'.format(rec.protocol, rec.ip, rec.port)
        if details:
            _op = '{:>6} → {}:{}'
        log.debug(_op)
        if is_alive:
            xc.is_proxy_alive_byip138(rec)


if __name__ == '__main__':
    run()
