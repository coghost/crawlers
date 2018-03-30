#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '15/12/2017 5:40 PM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''

import os
import sys
from urllib.request import urljoin

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

import click
from logzero import logger as log
from izen import helper

from base.crawl import Crawl
from base import abc

M = {
    'index': 'http://wiki.friendlyarm.com/',
    'main': 'http://wiki.friendlyarm.com/wiki/index.php/Main_Page',
    'ops_index': 'http://www.kuaidaili.com/ops/proxylist/{}/',
    'refer': 'http://wiki.friendlyarm.com',
}


class Fri(Crawl):
    def __init__(self,
                 refer=M.get('refer', ''),
                 parser='html5lib',
                 ):
        Crawl.__init__(self, refer,
                       parser=parser)

    def main_page(self):
        raw = self.bs4markup(self.do_get(M['main']))
        npc = raw.find('div', id='NanoPCSeries')
        _table = npc.next_sibling.next_sibling
        dat = []
        for li_ in _table.find_all('li'):
            dat.append({
                'name': li_.text,
                'url': urljoin(M['index'], li_.a.get('href') + '/zh')
            })
        return dat

    def pc_detail(self, url, simple):
        _id__ = '.E8.B5.84.E6.BA.90.E7.89.B9.E6.80.A7'
        params = {
            'url': url,
            'timeout': 10,
        }
        raw = self.bs4markup(self.do_get(params))

        def filter_it(txt):
            if not simple:
                return txt

            needed = 'CPU,DDR3,SD,eMMC,USB,SD'.lower().split(',')
            if any([txt.lower().find(x) != -1 for x in needed]):
                return txt

        def hardware_info(raw):
            mw_head = raw.find('span', id=_id__)
            if not mw_head:
                return '资源特性: 未找到'
            ul = mw_head.parent.next_sibling.next_sibling
            dat = []
            for li in ul.find_all('li'):
                if filter_it(li.text):
                    dat.append(li.text)

            return dat

        def gpio_info(raw_markup):
            tables = raw_markup.find_all('table', 'wikitable')
            gpio = tables[0]

            trs = gpio.find_all('tr')
            if not trs:
                return ''
            th = [x.text.replace('\n', '').lstrip().rstrip() for x in trs[0].find_all('td')]
            gpios = [[] for _ in range(len(th))]
            table = helper.TermTable(th)

            for tr in trs[1:]:
                info_ = [
                    x.text.replace('\n', '').lstrip().rstrip() for x in tr.find_all('td')
                ]

                for i, x in enumerate(info_):
                    gpios[i].append(x)

            for i, k in enumerate(th):
                table.add_data(k, gpios[i])
            return table

        gpio_table = gpio_info(raw)
        hard = hardware_info(raw)
        return hard, gpio_table


click_hint = '{}\nUSAGE: <cmd> {}'


@click.command()
@click.option('--name', '-n',
              help=click_hint.format('依据名字过滤, 不区分大小写', '-n <name>'))
@click.option('--simple', '-s',
              is_flag=True,
              help=click_hint.format('只显示最简信息<cpu/ram/emmc>', '-s'))
def run(name, simple):
    fri = Fri()
    pcs = fri.main_page()
    if name:
        pcs = [x for x in pcs if x['name'].lower().find(name.lower()) != -1]

    c = 'b'
    while c in 'b,B'.split(','):
        c = helper.num_choice([
            x['name'] for x in pcs
        ])

        if c in range(len(pcs)):
            pc = pcs[c]
            arm_info = fri.pc_detail(pc['url'], simple)
            if not arm_info:
                arm_info = ['未找到,请查看web: {}'.format(pc['url'])]

            hd_info, gpio_table = arm_info
            if not simple:
                print(gpio_table)

            helper.pause_choice(
                '{}\n{}\n{}'.format('*' * 64, '\n'.join(hd_info), '*' * 64),
                fg_color='cyan')
            # abc.color_print('_' * 32)

            c = 'b'


if __name__ == '__main__':
    run()
