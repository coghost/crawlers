# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '26/10/2017 9:56 AM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''

import os
import sys
from functools import wraps
import random
import base64

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import requests
import logzero
from logzero import logger as log

from izen import helper

from bs4 import BeautifulSoup
from config import Conf, LFormatter
from clint import textui

cfg = Conf().cfg

# 检查日志配置, 是否写入文件
if cfg.get('log.enabled', False):
    logzero.logfile(
        cfg.get('log.file_pth', '/tmp/igt.log'),
        maxBytes=cfg.get('log.file_size', 5) * 1000000,
        backupCount=cfg.get('log.file_backups', 3),
        loglevel=cfg.get('log.level', 10),
    )

# bagua = '☼✔❄✖✄'
# bagua = '☰☷☳☴☵☲☶☱'  # 乾(天), 坤(地), 震(雷), 巽(xun, 风), 坎(水), 离(火), 艮(山), 兑(泽)
bagua = '🍺🍻♨️️😈☠'
formatter = LFormatter(bagua)
logzero.formatter(formatter)
click_hint = '{}\nUSAGE: <cmd> {}'


def update_cfg(key, val):
    cfg[key] = val
    cfg.sync()


def bs4markup(params=None):
    """
        **format the markup str to BeautifulSoup doc.**

    .. code:: python

        @bs4markup
        def fn():
            pass

    :rtype: BeautifulSoup
    :param params: ``{'parser': 'html5lib'}``
    :return:
    """
    params = params or {}

    def dec(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                rs = fn(*args, **kwargs)
                markup = BeautifulSoup(
                    rs,
                    params.get('parser', 'html5lib'),
                )
                # 如果 rs 的值与 markup.text 相同, 则判定为非 html markup 标记, 直接返回原值
                if rs == markup.text:
                    return rs
                else:
                    return markup
            except TypeError as _:
                pass

        return wrapper

    return dec


def save_img(dat, pth):
    if not dat:
        return
    helper.write_file(dat, pth)


def add_jpg(pathin):
    if not os.path.exists(pathin):
        log.debug('{} not exist'.format(pathin))
        return

    for root, dirs, files in os.walk(pathin):
        for f in files:
            ext = f.split('.')
            _fpth = os.path.join(root, f)
            if len(ext) != 1:
                if ext[-1] == 'jpg':
                    print('skip', _fpth)
                    continue

            os.rename(_fpth, '{}.jpg'.format(_fpth))


def randint(start=0, end=100):
    return random.randint(start, end)


def force_quit():
    """
        call os._exit(-1) to force quit program.

    :return:
    :rtype:
    """
    os._exit(-1)


if __name__ == '__main__':
    # cat_net_img()
    orig = '今天是一个好天气'
    s = helper.multi_replace(orig, '今天,today |是,is |好天气,good weather')
    print(s)
