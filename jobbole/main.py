# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '27/11/2017 11:45 AM'
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

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from logzero import logger as log
import click
from tqdm import tqdm

from base.crawl import Crawl
from base import abc

My = {
    'refer': 'www.jobole.com',
    'py': 'http://hao.jobbole.com/?catid=144',
}


class Jobb(Crawl):
    def __init__(self, refer=My.get('refer', ''), encoding='utf-8'):
        Crawl.__init__(self, refer, encoding=encoding)
        self.soft = None
        self.soft_flatten = None
        self.soft_count = ''

    def load_cache(self):
        self.soft = json.loads(abc.read_file('jobble.json'))
        self.soft_flatten = json.loads(abc.read_file('jobble.flat.json'))
        self.soft_count = '分类:{}, 总数:{}'.format(len(self.soft), len(self.soft_flatten))

    def update_cache(self):
        pyres = self.main_page()
        flat = []

        for nfr in tqdm(pyres, ascii=True):
            if nfr.get('sub_res'):
                flat += nfr.get('sub_res')
                continue

            items = self.sub_page(nfr.get('url'))
            items = sorted(items, key=lambda s: s['name'])
            nfr['sub_res'] = items
            flat += nfr.get('sub_res')

        abc.write_file(json.dumps(pyres).encode(), 'jobble.json')
        abc.write_file(json.dumps(flat).encode(), 'jobble.flat.json')

    def main_page(self):
        raw = self.bs4get(My.get('py'))
        list_rs_raw = raw.find('div', 'list-rs')
        list_rs = []

        for lrx in list_rs_raw.find_all('div', 'lr-box lr-box-nav'):
            if not lrx:
                continue
            resources = lrx.ul.find_all('li')
            rss = []
            if len(resources) < 6:
                for res in resources:
                    rss.append({
                        'name': res.h3.text,
                        'url': res.a.get('href'),
                        'desc': res.p.text
                    })
            list_rs.append({
                'name': lrx.h2.text,
                'url': lrx.h2.a.get('href'),
                'sub_res': sorted(rss, key=lambda s: s['name']),
            })

        return list_rs

    def sub_page(self, url):
        """
        1. 只有一个页面内容
        2. 多个页面
        :param url:
        :return:
        """
        # url, items = self.single_page(url)
        all_page_items = []
        while url:
            url, items = self.single_page(url)
            # print(url)
            all_page_items += items

        return all_page_items

    def single_page(self, url):
        raw = self.bs4get(url)
        lr_item_raw = raw.find('div', 'lr-box').find_all('li', 'res-item')
        lr_items = []
        page_next_raw = raw.find('ul', 'pagination p-paging').find_all('li')
        for itm in lr_item_raw:
            if not itm:
                continue
            lr_items.append({
                'name': itm.h3.text,
                'url': itm.h3.a.get('href'),
            })

        next_page_url = ''
        for pgn in page_next_raw:
            alink = pgn.find('a')
            if alink and alink.text.find('下一页') != -1:
                next_page_url = alink.get('href')
        return next_page_url, lr_items

    def search_by_name(self, name):
        if not self.soft_flatten:
            self.load_cache()
        name = name.lower()
        flat = self.soft_flatten
        cand_soft = [
            x for x in flat
            if x.get('name').lower().find(name) != -1
        ]
        if len(cand_soft) == 1:
            return cand_soft

        if not len(cand_soft):
            return None
        cho = abc.num_choice(cand_soft)
        return cand_soft[cho]


@click.command()
@click.option('--name', '-n',
              help='find by the name\nUSAGE: <cmd> -n <name>')
@click.option('--count', '-c',
              is_flag=True,
              help='display the count of jobble libs\nUSAGE: <cmd> -n <name>')
@click.option('--all_libs', '-a',
              is_flag=True,
              help='list all available\nUSAGE: <cmd> -a')
@click.option('--update', '-u',
              is_flag=True,
              help='update local cache\nUSAGE: <cmd> -u')
def run(update, name, all_libs, count):
    jobb = Jobb()

    if update:
        jobb.update_cache()
        os._exit(-1)
    jobb.load_cache()

    if count:
        log.debug(jobb.soft_count)
        os._exit(-1)

    if name:
        v = jobb.search_by_name(name)
        log.debug('{}'.format(v if v else 'Nothing found!!!'))
        os._exit(-1)

    if all_libs:
        soft_jobb = jobb.soft
        c1 = abc.num_choice([s.get('name') for s in soft_jobb])
        cho = soft_jobb[c1]

        i = abc.num_choice([c.get('name') for c in cho['sub_res']])
        log.debug('[{}]({})'.format(cho['sub_res'][i]['name'], cho['sub_res'][i]['url']))


if __name__ == '__main__':
    pass
    run()
