# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '05/12/2017 11:26 AM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''

import os
import sys
import unittest
import json

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

from base.crawl import Crawl

from base import dbstore
from base.dbstore import rds


class BaseTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_rds(self):
        rdb_out = dbstore.rdc()
        # 初始化一个字典
        icw = rds.Dict(client=rdb_out, key='ig.crawlers')
        # 更新, 自动写入 redis
        icw['fns'] = json.dumps({
            'base': 10,
            'crx': 2,
            'jobbole': 1,
        })
        # 删除字典
        icw.clear()


if __name__ == '__main__':
    unittest.main()
