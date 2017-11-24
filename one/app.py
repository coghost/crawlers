# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '06/11/2017 4:01 PM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''

import os
import sys

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from logzero import logger as log
import bs4
from tqdm import tqdm
import click
import json
from multiprocessing import Pool

from base.crawl import Crawl
from base import abc
from base.abc import cfg

M = {
    'index': 'http://wufazhuce.com/',
}


class One(Crawl):
    def __init__(self, base_dir='/tmp/one'):
        Crawl.__init__(self, refer=M['index'])
        self.base_dir = base_dir

    def init(self):
        pass


def run():
    one = One()


if __name__ == '__main__':
    run()
