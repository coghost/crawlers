# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '06/12/2017 2:38 PM'
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

from mongoengine import *
from base import dbstore


class Proxies(Document):
    """ xici 代理信息

    """
    country = StringField()
    ip = StringField()
    port = IntField()
    location = StringField()
    anonymity = StringField()
    protocol = StringField()
    speed = StringField()
    method = StringField()
    conn_time = StringField()
    alive = StringField()
    checked = StringField()

    meta = {
        'db_alias': dbstore.mg_cfg.get('alias'),
        'collection': 'xici.proxies',
        'ordering': [
            '-checked'
        ],
        'indexes': [
            {
                'fields': ['ip', 'port'],
                # 'unique': True,
            },
            '-country',
            'ip',
            'port',
            '-location',
            '-anonymity',
            '-protocol',
            '-speed',
            '-conn_time',
            '-alive',
            '-checked',
        ],
    }


def save_it(dat):
    p = Proxies()
    for k, v in dat.items():
        p[k] = v

    try:
        p.save()
    except NotUniqueError as _:
        print(_)


