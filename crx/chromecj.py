# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '07/11/2017 3:16 PM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''

import os
import sys
from urllib.parse import urljoin, urlencode
import time

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from logzero import logger as log
from tqdm import tqdm
import click
import json
from multiprocessing import Pool

from base.crawl import Crawl
# from base import abc
from base.abc import cfg

from izen import helper

import requests

M = {
    'refer': 'http://chromecj.com',
    'index': 'http://chromecj.com/',
    'search': 'http://chromecj.com/handler/search/',
}


class Crx(Crawl):
    def __init__(self):
        Crawl.__init__(self, refer=M['refer'])

    def search(self, name=''):
        """
            name/ url
        :param name:
        :return:
        """
        r = self.stream_post({
            'url': 'http://chromecj.com/handler/search/{}'.format(name)
        })
        r = helper.to_str(r)
        dat = []
        for cj in r.split('|'):
            info = cj.split('^')
            # id, name, type, desc, img, date
            dat.append({
                'cid': info[0],
                'name': info[1],
                'desc': info[3],
                'url': urljoin(M['index'], '/{}/{}/{}.html'.format(info[2], info[-1][:7], info[0]))
            })
        return dat


@click.command()
@click.option('--name', '-n',
              help='find by the name\nUSAGE: <cmd> -n <name>')
def run(name):
    crx = Crx()
    pages = crx.search(name)
    choice_list = []
    # if True:
    #     choices = [
    #         '({})[{}]'.format(x['name'], x['desc'])
    #         for x in pages
    #     ]
    # else:
    _ = [
        '{}'.format(x['name'])
        for x in pages
    ]
    choice_list.append(_)
    while choice_list:
        c = helper.num_choice(choice_list[-1])
        if str(c) in 'bB' and len(choice_list) == 1:
            continue

        choice_list.pop()
        _url = 'http://chromecj.com/Handler/Download/{}'.format(pages[c]['cid'])
        rs = os.popen('wget {} -O /tmp/{}_{}.zip'.format(_url, pages[c]['name'], pages[c]['cid']))
        print('download {}'.format(rs))


if __name__ == '__main__':
    run()
