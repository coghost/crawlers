#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '16/12/2017 11:52 PM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''

import os
import sys
import time
import json
from urllib.request import unquote

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

import wget

from logzero import logger as log
import click
from tqdm import tqdm
from izen import helper
from base.crawl import Crawl

from base import abc
from base.abc import cfg

import requests

M = {
    'refer': 'http://course.dongao.com',
    'login': 'http://passport.dongao.com/login',
    'practice': 'http://course.dongao.com/catalog/{}',
    'lecture_doc': 'http://course.dongao.com/catalog/handout/down',
    'lecture_mp3': 'http://course.dongao.com/catalog/mp3/down',  # post, lectureId:6736
}

base_pth = '/Users/lihe/Documents/mylqy/dongao2017'
catalog = {
    '1268': {
        'cate': 'lesson',
        'name': '基础班-刘忠',
    },
    '1271': {
        'cate': 'example',
        'name': '习题班-刘忠',
    },
    '1280': {
        'cate': 'lesson',
        'name': '基础班-王颖',
    },
    '1281': {
        'cate': 'example',
        'name': '习题班-王颖',
    },
}


class Da(Crawl):
    def __init__(self,
                 refer=M.get('refer', ''),
                 catalog_index='',
                 ):
        Crawl.__init__(self, refer)
        self.get_headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0',
        }
        self.post_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0',
            'Referer': M['refer'],
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        self.sess = requests.session()

        if catalog_index:
            self.catalog_info = {
                'index': catalog_index,
                'info': catalog[catalog_index],
                'base_pth': os.path.join(base_pth, catalog[catalog_index]['name']),
                'url': M['practice'].format(catalog_index),
                'cache_file': 'da2017_{}.txt'.format(catalog_index)
            }
        self.da2017 = []

    def login(self):
        """
        dest	'phone'
        password	'md5(pwd)'
        autoLogin	0
        validateCode
        :return:
        :rtype:
        """
        form = {
            'dest': cfg.get('dongao.dest'),
            'password': cfg.get('dongao.password'),
            'autoLogin': 0,
        }
        self.sess.post(M['login'], data=form, headers=self.post_headers)
        self.dump_cookies(self.sess.cookies)

    @staticmethod
    def is_login(raw):
        login_box = raw.find('div', 'login_box')
        return not login_box

    def fetch_chapters(self):
        raw = self.sess.get(self.catalog_info['url'], headers=self.get_headers)
        raw = self.bs4markup(raw.text, parser='html5lib')
        if not self.is_login(raw):
            log.error('login first')
            abc.force_quit()

        chaps = []

        if self.catalog_info['info']['cate'] == 'lesson':
            have_chapter = raw.find('div', 'havechapter')
            li_list = have_chapter.find_all('li')
            for li_ in li_list:
                _lid = li_.get('lectureid')
                if _lid:
                    d = {
                        'lid': _lid,
                        'name': helper.multi_replace(li_.span.text, '\n|\t| |\xa0\xa0,-'),
                    }
                    chaps.append(d)
        else:
            uls = raw.find_all('ul', 'chapter chapte_child chapter_open')
            for ul in uls:
                li_ = ul.find('li')
                _lid = li_.get('lectureid')
                if _lid:
                    d = {
                        'lid': _lid,
                        'name': helper.multi_replace(li_.span.text, '\n|\t| |\xa0\xa0,-'),
                    }
                    chaps.append(d)

        return chaps

    def gen_lesson_url(self, chapters):
        dat = []
        for chap in tqdm(chapters, ascii=True):
            # get mp3 url
            res = self.sess.post(M['lecture_mp3'], data={'lectureId': chap['lid']})
            cp = {
                'lid': chap['lid'],
                'name': chap['name'],
                'mp3': unquote(res.json()['obj']),
            }
            time.sleep(1)

            # get doc url
            res = self.sess.post(M['lecture_doc'], data={'lectureId': chap['lid']})
            cp['doc'] = unquote(res.json()['obj'])
            dat.append(cp)

            rd = abc.randint(1, 3)
            log.debug('sleep {}'.format(rd))
            time.sleep(rd)

        helper.write_file(json.dumps(dat), self.catalog_info['cache_file'])

    def load_chapters(self):
        if helper.is_file_ok(self.catalog_info['cache_file']):
            self.da2017 = json.loads(helper.to_str(helper.read_file(self.catalog_info['cache_file'])))

    def download(self):
        if not self.da2017:
            self.load_chapters()

        def down(lec, which_type):
            """"""
            if which_type not in ['mp3', 'doc']:
                log.warn('Not Supported of ({})'.format(which_type))
                return

            save_name = os.path.join(self.catalog_info['base_pth'], which_type, '{}.{}'.format(lec['name'], which_type))
            helper.mkdir_p(save_name)
            if helper.is_file_ok(save_name):
                print()
                log.debug('SKIP {}'.format(save_name))
                return
            # 默认等待2s, 如果是下载 mp3 随机等待
            rd = 2
            if which_type == 'mp3':
                rd = abc.randint(3, 6)

            url = lec[which_type]
            log.debug('[WAIT] {}s for ({}:{})...'.format(rd, save_name, url))
            time.sleep(rd)
            wget.download(url, out=save_name)

        for lec in tqdm(self.da2017, ascii=True):
            down(lec, 'doc')
            down(lec, 'mp3')


click_hint = '{}\nUSAGE: <cmd> {}'


@click.command()
@click.option('--catalog_index', '-c',
              type=str,
              help=click_hint.format('课程id: 1271=习题, 1268=基础', '-c <index>'))
@click.option('--login', '-lg',
              is_flag=True,
              help=click_hint.format('手动登陆', ' -lg'))
@click.option('--lesson', '-l',
              is_flag=True,
              help=click_hint.format('获取课程列表', ' -l'))
@click.option('--down', '-d',
              is_flag=True,
              help=click_hint.format('开始下载', ' -d'))
@click.option('--show', '-s',
              is_flag=True,
              help=click_hint.format('显示所有课程', ' -s'))
def run(catalog_index, login, lesson, down, show):
    if login:
        da = Da()
        da.login()
        abc.force_quit()

    if not catalog_index or catalog_index not in catalog.keys():
        log.error('catalog index needed: [{}]'.format(','.join(catalog.keys())))
        abc.force_quit()

    da = Da(catalog_index=catalog_index)

    da.sess.cookies = da.load_cookies()
    da.load_chapters()

    if show:
        helper.num_choice([
            '{}({})'.format(x['name'], ','.join(x.keys()))
            for x in da.da2017
        ])

    if lesson:
        chaps = da.fetch_chapters()
        da.gen_lesson_url(chaps)

    if down:
        da.download()


if __name__ == '__main__':
    run()
