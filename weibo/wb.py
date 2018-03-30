#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '11/12/2017 10:20 AM'
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
from urllib.parse import urljoin, urlencode, quote
import re
import base64
import time
import functools

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import rsa
import binascii

from logzero import logger as log
import logzero
import click
from tqdm import tqdm
from izen import helper
from base.crawl import Crawl

from base import abc
from base import dbstore
from base.abc import cfg

from weibo import wb_mg_doc

import requests

M = {
    'refer': 'https://weibo.com/',
    'pre_login': 'https://login.sina.com.cn/sso/prelogin.php',
    'login': 'https://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.19)',
    'search_user': 'http://s.weibo.com/user/{}&page={}',
    'profile': 'https://weibo.com/{}/profile?topnav=1&wvr=6&is_all=1',
    'info': 'https://weibo.com/{}/info',
    'album': 'http://photo.weibo.com/albums/get_all',
    'photo': 'http://photo.weibo.com/photos/get_all',
    'big_img': 'http://wx1.sinaimg.cn/large/{}.jpg',
    'get_my_follow': 'https://weibo.com/p/{}/myfollow',
    'get_follow': 'https://weibo.com/p/{}/follow',
    'get_my_fans': '',
    'get_fans': '',
    # 'do_follow': 'http://s.weibo.com/ajax/user/follow',
    'do_follow': 'https://weibo.com/aj/f/followed?ajwvr=6',
    'do_add_group': 'http://s.weibo.com/ajax/user/addUserToGroup',
    'undo_follow': 'https://weibo.com/aj/f/unfollow',  # ?ajwvr=6
}


class Wb(Crawl):
    def __init__(self,
                 refer=M.get('refer', ''),
                 big_head=False, img_cache_dir='/tmp/weibo', img_height=6, use_cache=True,
                 ):
        Crawl.__init__(self, refer)
        self.get_headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0',
        }
        self.post_headers = {
            'Host': 'login.sina.com.cn',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://weibo.com/',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        self.json_header = {
            "Content-Type": "application/x-www-form-urlencoded",
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0',
            'Host': 'weibo.com',
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://weibo.com',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        self.sess = requests.session()
        self.domid = ''
        self.big_head = big_head
        self.img_cache_dir = os.path.join(img_cache_dir, 'large' if big_head else 'little')
        self.img_height = img_height
        self.use_cache = use_cache
        self.cached_users_followed = []
        self.cached_users_followed_index = 0

        self.personal_info = {}

    def cat_net_img(self, pic_url, indent=4):
        """
            封装了 ``helper.cat_net_img`` 的偏函数, 方便使用本地配置参数

        :param pic_url:
        :type pic_url:
        :param indent:
        :type indent:
        :return:
        :rtype:
        """
        if self.big_head:
            pic_url = self.use_big_head(pic_url, use_big=True)

        functools.partial(helper.cat_net_img,
                          img_height=self.img_height,
                          img_cache_dir=self.img_cache_dir,
                          use_cache=self.use_cache)(url=pic_url, indent=indent)

    def use_big_head(self, img_url, use_big=False):
        if not img_url.startswith('http:'):
            img_url = 'http:' + img_url

        if use_big and self.big_head:
            img = img_url.split('/')
            img[-2] = 'large'
            img_url = '/'.join(img)

        return img_url

    @staticmethod
    def gen_rsa(dat, password=''):
        rp = int(dat.get('pubkey'), 16)
        key = rsa.PublicKey(rp, 65537)
        msg = '{}\t{}\n{}'.format(dat.get('servertime'), dat.get('nonce'), password)
        msg = helper.to_bytes(msg)
        sp = rsa.encrypt(msg, key)
        sp = binascii.b2a_hex(sp)
        return sp

    def pre_login(self, username='', password=''):
        params = {
            'entry': 'weibo',
            'su': base64.b64encode(helper.to_bytes(username))[:-1],
            'rsakt': 'mod',
            'checkpin': 1,
            'client': 'ssologin.js(v1.4.19)',
            '_': helper.unixtime(mm=True)
        }
        raw = self.sess.get(M['pre_login'], params=params, headers=self.get_headers)
        dat = json.loads(raw.content)

        _sp = self.gen_rsa(dat, password=password)
        rt = {
            'servertime': dat['servertime'],
            'nonce': dat['nonce'],
            'rsakv': dat['rsakv'],
            'su': params['su'],
            'sp': _sp,
        }
        return rt

    @staticmethod
    def dump_person_config(txt):
        """
            保存个人登陆信息到本地缓存

        :param txt:
        :type txt:
        :return:
        :rtype:
        """
        txt = [t[1:].rstrip() for t in txt.split('\n') if t and t.find('CONFIG') != -1 and t.find('var ') == -1]
        dat = {}
        keys = ['oid', 'page_id', 'uid', 'nick', 'sex', 'watermark', 'domain', 'avatar_large', 'pid']
        for t in txt:
            k, v = t[:-1].split('=')
            k = k.split('\'')[1]
            if k not in keys:
                continue
            dat[k] = v.replace('\'', '') if k != 'avatar_large' else 'http:' + v.replace('\'', '')
        return dat

    def login(self, username='', password=''):
        form = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'qrcode_flag': False,
            'useticket': '1',
            'pagerefer': 'https://login.sina.com.cn/crossdomain2.php?action=logout&r=https%3A%2F%2Fweibo.com%2Flogout.php%3Fbackurl%3D%252F',
            'vsnf': 1,
            'service': 'miniblog',
            'pwencode': 'rsa2',
            'sr': '1280*800',
            'encoding': 'UTF-8',
            'prelt': '41',
            'url': 'https://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META',
            'sp': '3d841d27085a2fac6f5218f18f4ce5caf3cb020c49bc109608dc106f3e14cf8354e41ad03444672f492b490f81f155fff9364f2dff86677429e5b745fbe4ccffadd5458a0a6f29a5d769c63801753b49b3eaf7b52489da04a79f0724b9842c9aac7f546d2eb037d44484bd0ad3c8ac35ba9136a1eceaaa59587168881dc06f3b',
            'servertime': '1512958714',
            'nonce': 'ZIVLK5',
            'rsakv': '1330428213',
        }
        dat = self.pre_login(username=username, password=password)
        form = dict(form, **dat)

        log.debug('STEP1: get {}'.format(M['login']))
        res = self.sess.post(M['login'], data=form, headers=self.post_headers)

        # 分析 login.php 返回信息的重定向 url
        pa = r'location\.replace\([\'"](.*?)[\'"]\)'
        loop_url = re.findall(pa, res.content.decode('GBK'))[0]
        log.debug('STEP2: get {}'.format(loop_url))
        # 获取返回第一次重定向 url 的返回信息
        res = self.sess.get(loop_url)
        # 返回信息分两部分, 第一部分 setCrossDomainUrlList 出现 302 Moved Temporarily 错误, 故跳过
        # 只取返回信息的第二部分 解析方式同 login.php 返回结果
        final_url = re.findall(pa, res.content.decode('GBK'))[0]
        log.debug('STEP3: get {}'.format(final_url))

        res = self.sess.get(final_url)
        uuid_pa = r'"uniqueid":"(.*?)"'
        uuid_res = re.findall(uuid_pa, res.text, re.S)[0]
        log.debug('STEP4:user_id: {}'.format(uuid_res))

        url = M['profile'].format(uuid_res)
        raw = self.sess.get(url)

        def get_config(raw_mark):
            _START = '<!-- $CONFIG -->'
            _END = '<!-- / $CONFIG -->'
            return raw_mark.split(_START)[1].split(_END)[0]

        user_config = get_config(raw.text)
        user_config = self.dump_person_config(user_config)
        helper.write_file(json.dumps(user_config), 'personal.txt')

        raw = self.bs4markup(raw.text)

        log.debug('STEP5: title : {}'.format(raw.find('title').text))
        abc.update_cfg('weibo.nickname', raw.find('title').text.replace('的微博_微博', ''))
        log.info('[LOGIN:SUCCESS] {}({})'.format(cfg.get('weibo.nickname'), username))

        self.dump_cookies(self.sess.cookies)

    def update_personal_info(self):
        line_id = '"ns":"","domid":"Pl_Core_T8CustomTriColumn__'
        user_raw = self.do_get_weibo_stk_to_html(
            M['info'].format(self.personal_info.get('uid')),
            patten_id=line_id
        )
        person_num = ''
        for lk in user_raw.find_all('a'):
            person_num += lk.text
        person_num = helper.multi_replace(person_num, '\n|关注,/|粉丝,/|微博')
        wb_mg_doc.user_update({
            'uid': self.personal_info.get('uid'),
            'person_num': person_num,
        })

    def who_am_i(self):
        person_info = json.loads(helper.read_file('personal.txt'))
        self.personal_info = person_info
        if not person_info:
            log.error('Login to get your person info first!!!')
            abc.force_quit()

    def is_cookie_ok(self):
        url = 'http://photo.weibo.com/albums/get_all?uid=6069778559&page=1&count=20'
        print(url)
        rs = self.sess.get(url, headers=self.get_headers)
        if rs.history and rs.history[0].status_code == 302:
            # if not rs.status_code == 200:
            log.warn('session Expired, relogin.')
            self.login()
            os._exit(-1)
        else:
            log.debug('session is ok!!!')

    def update_albums(self, uid='1915268965'):
        """
            依据 ``uid`` 来获取该用户的所有照片, 并同步写入数据库中.
            专辑数量较小, 且专辑内图片数量一直更新, 故需要采取每次更新的方式写入

        :param uid:
        :type uid: str/dict
        :return:
        :rtype:
        """
        if isinstance(uid, dict):
            uid = uid['uid']

        page_count = cfg.get('weibo.album_page_count', 20)
        params = {
            'uid': uid,
            'count': page_count,
        }

        def fetch_album(page):
            page['index'] += 1
            params['page'] = page['index']
            raw = self.sess.get(M['album'], params=params, headers=self.get_headers)

            albums_dat = raw.json()
            albums = albums_dat['data']
            _total_albums = albums['total']

            page['updated'] += len(albums['album_list'])

            for album_ in albums['album_list']:
                wb_mg_doc.album_update(album_)

            return albums['album_list'] == _total_albums

        page = {
            'index': 0,
            'updated': 0,
        }
        log.debug('Try Update ({})'.format(uid))
        while fetch_album(page):
            fetch_album(page)
            time.sleep(abc.randint(5, 9))

        log.debug('Success update ({}) albums info'.format(page['updated']))

    def update_photos(self, album_info, init_photos=False):
        """
            获取某个专辑下的所有照片信息, 并写入数据库中.

            - 如果是初始化, 则批量写入, 忽略错误.
            - 否则, 更新模式, 只更新大于查询最后一次记录的时间戳的数据

        :param album_info:
        :type album_info: dict
        :param init_photos: 是否初始化
        :type init_photos:
        :return:
        :rtype:
        """
        page_count = cfg.get('weibo.photo_page_count', 32)
        params = {
            'uid': album_info['uid'],
            'album_id': album_info['album_id'],
            'type': album_info.get('album_type', 3),
            'count': page_count,
            'page': 1,
        }
        # 如果更新相册照片时异常结束, 则会从最后一次有效记录位置开始更新
        # TODO: 修改为保持进度到数据库中.
        _max_page = album_info['count']['photos'] // page_count

        # 最后一次更新的时间戳, 设置为0, 可以获取所有数据
        latest_ts = 0

        if not init_photos:
            # 如果不是初始化, 则尝试从数据库获取
            last_doc = wb_mg_doc.WeiboPhotos.objects(
                __raw__={
                    'album_id': album_info['album_id']
                }
            ).first()
            if last_doc:
                latest_ts = last_doc.timestamp

        # start = 0
        while True:
            suc = 'DONE'
            # start += 1
            # params['page'] = start
            raw = self.sess.get(M['photo'], params=params, headers=self.get_headers)
            log.debug('try crawl: {}'.format(raw.url))

            photos = raw.json()
            raw_p_list = photos['data']['photo_list']

            # 如果非初始化模式, 则依据时间戳过滤掉已经下载的记录
            if init_photos:
                p_list = raw_p_list
            else:
                p_list = [
                    x for x in raw_p_list
                    if x['timestamp'] > latest_ts
                ]
            if not p_list:
                log.debug('All records has Updated already!!!')
                return

            aff_row = dbstore.batch_write(p_list, 'weibo.photo.details')

            # 非初始化模式下,
            if not init_photos:
                # 如果原始数据与过滤后的数据长度不一致, 则已经更新到最新记录.
                if len(p_list) != len(raw_p_list):
                    log.info('All Photos records updated!!!')
                    return
                # 如果待更新的记录与实际更新记录数目不相同也为已更新到最新记录
                if len(p_list) != aff_row:
                    log.info('DONE@ ({}/{})'.format(len(p_list), aff_row))
                    return

            if not aff_row:
                suc = 'SKIP'

            # 如果当前页面数与最大值相同, 则结束
            if params['page'] >= _max_page:
                return

            # 使用等待延迟, 防止快速爬取导致被禁止
            _ri = abc.randint(2, 7)
            log.debug('{}: ({}) {}/{}, and sleep {}s'.format(suc, len(p_list), params['page'], _max_page, _ri))
            params['page'] += 1
            for _ in tqdm(range(_ri), ascii=True, desc='sleep {}s'.format(_ri)):
                time.sleep(1)

    def do_get_weibo_stk_to_html(self, url, params=None, patten_id=''):
        if params:
            raw = self.sess.get(url, params=params)
        else:
            raw = self.sess.get(url)

        txt = ''
        for line in raw.text.split('\n'):
            if line.find(patten_id) != -1:
                txt = line
                break

        user_raw = self.stk_view_js_to_html(txt)
        user_raw = self.bs4markup(user_raw)

        return user_raw

    def stk_view_js_to_html(self, dat):
        """
            转换 ``weibo stk js`` 为可识别的 html Markup

            输出:
            <div class="list_person clearfix">
                <div class="person_pic">
                    <a target="_blank" href="//weibo.com/u/1915268965?refer_flag=1001030201_" title="霹雳无敌李三娘" suda-data="key=tblog_search_user&value=user_feed_1_icon"><img class="W_face_radius" src="//tvax1.sinaimg.cn/crop.0.0.1242.1242.180/7228af65ly8fmc4jx2rwij20yi0yi419.jpg" uid="1915268965" height="80" width="80"/></a>
                </div>
                <div class="person_detail">
                    <p class="person_name">
                        <a class="W_texta W_fb" target="_blank" href="//weibo.com/u/1915268965?refer_flag=1001030201_" title="霹雳无敌李三娘" uid="1915268965" suda-data="key=tblog_search_user&value=user_feed_1_name">
                            霹雳无敌<em class="red">李三娘</em>
                        </a>
                        <a target="_blank" href="//verified.weibo.com/verify" title= "微博个人认证 " alt="微博个人认证 " class="W_icon icon_approve"></a><a href="//vip.weibo.com/personal?from=search" target="_blank" title="微博会员"><i class="W_icon ico_member4"></i></a>
                    </p>
                    <p class="person_addr">
                        <span class="female m_icon" title="女"></span>
                        <span>其他</span>
                        <a class="W_linkb" target="_blank" href="//weibo.com/u/1915268965?refer_flag=1001030201_" class="wb_url" suda-data="key=tblog_search_user&value=user_feed_1_url">//weibo.com/u/1915268965</a>
                    </p>
                    <p class="person_card">
                        知名萌宠博主 萌宠视频自媒体
                    </p>
                    <p class="person_num">
                        <span>关注<a class="W_linkb" href="//weibo.com/1915268965/follow?refer_flag=1001030201_" target="_blank" suda-data="key=tblog_search_user&value=user_feed_1_num">333</a></span>
                        <span>粉丝<a class="W_linkb" href="//weibo.com/1915268965/fans?refer_flag=1001030201_" target="_blank" suda-data="key=tblog_search_user&value=user_feed_1_num">10万</a></span>
                        <span>微博<a class="W_linkb" href="//weibo.com/1915268965/profile?refer_flag=1001030201_" target="_blank" suda-data="key=tblog_search_user&value=user_feed_1_num">3319</a></span>
                    </p>
                        <div class="person_info">
                            <p>简介：
                                天天被儿砸殴打的老母亲
                            </p>
                        </div>
                        <p class="person_label">标签：
                            <a class="W_linkb" href="&tag=%25E5%25A4%25A9%25E7%25A7%25A4%25E5%25BA%25A7&Refer=SUer_tag" suda-data="key=tblog_search_user&value=user_feed_1_label">
                                天秤座
                            </a>
                            <a class="W_linkb" href="&tag=%25E5%25A6%2596%25E5%25AD%25BD&Refer=SUer_tag" suda-data="key=tblog_search_user&value=user_feed_1_label">
                                妖孽
                            </a>
                            <a class="W_linkb" href="&tag=%25E9%2585%2592%25E9%25AC%25BC%25E4%25B8%2580%25E6%259E%259A&Refer=SUer_tag" suda-data="key=tblog_search_user&value=user_feed_1_label">
                                酒鬼一枚
                            </a>
                        </p>
                </div>
            </div>

        :param dat:
        :type dat:
        :return:
        :rtype:
        """
        raw = self.bs4markup(dat)
        dat = raw.find('script').text.split('{')[1].split('}')[0]
        dat = '{' + dat + '}'
        dat = json.loads(dat)
        self.domid = dat.get('domid')
        user_raw = dat.get('html')
        user_raw.replace('\n', '').replace('\t', '').replace('\/', '/')
        # user_raw = abc.multi_replace(user_raw, '\n|\t|\/')
        return user_raw

    @staticmethod
    def trim_mark(t_):
        if not t_:
            return ''
        return ': '.join(x.lstrip() for x in helper.multi_replace(t_.text, '\t|\n').lstrip().rstrip().split('：'))

    def do_search_user(self, dat, page_index=1):
        """
            依据名字查询对应的 uid, 然后依据微博返回结果分页显示, 每页20条

        :param dat:
        :type dat:
        :param page_index:
        :type page_index:
        :return:
        :rtype:
        """
        if isinstance(dat, dict):
            dat = dat.get('uid') or dat.get('name')
        if not dat:
            log.error('必须提供查找的账号信息<用户名/用户唯一编号>')
            return []
        dat = quote(dat.encode())
        user_raw = self.do_get_weibo_stk_to_html(
            M['search_user'].format(dat, page_index),
            patten_id='"pid":"pl_user_feedList"',
        )
        if not user_raw:
            return []

        _total_raw = user_raw.find('div', 'search_num')
        if _total_raw:
            log.debug('共计: {}'.format(_total_raw.text))

        users = []

        def user_raw_to_dict(mark):
            person_pic = self.use_big_head(mark.find('div', 'person_pic').a.img.get('src'))
            person_name_attrs = mark.find('p', 'person_name').find_all('a')

            approve = ''
            user_info = person_name_attrs[0]
            if len(person_name_attrs) > 1:
                approve = person_name_attrs[1]
                approve = helper.multi_replace(approve.get('title'), '微博|认证')

            person_card = mark.find('p', 'person_card')
            person_info = mark.find('div', 'person_info')
            person_label = mark.find('p', 'person_label')
            person_num = mark.find('p', 'person_num')
            person_num_txt = ''.join([x for x in person_num.text.split('\n') if x])
            person_addr = mark.find('p', 'person_addr')
            addrs = person_addr.find_all('span')

            userinfo = {
                'name': helper.multi_replace(user_info.get('title', ''), '\t|\n| '),
                'uid': user_info.get('uid', ''),
                'sex': 'm' if addrs[0].get('title') in ['男', 'male'] else 'f',
                'addr': addrs[1].text,
                'home_page': 'http:' + user_info.get('href', ''),
                'person_pic': person_pic,
                'person_card': self.trim_mark(person_card),
                'person_info': self.trim_mark(person_info),
                'person_label': self.trim_mark(person_label),
                'approve': approve.rstrip(),
                'person_num': helper.multi_replace(person_num_txt, '关注|粉丝,/|微博,/')
                # 'person_num': abc.multi_replace(person_num_txt, '关注,关注:|粉丝,粉丝:|微博,微博:')
            }
            return userinfo

        for user_info_raw in user_raw.find_all('div', 'list_person clearfix'):
            d = user_raw_to_dict(user_info_raw)
            users.append(d)

        return users

    @staticmethod
    def load_user_info(name, page_index=1):
        page_size = 20
        _end = page_index * page_size
        _start = _end - page_size

        users = wb_mg_doc.WeiboUsers.objects(
            name__icontains=name
        )[_start:_end]

        if not users:
            return {}
        d = []
        for user_ in users:
            d.append(user_._data)
        return d

    @staticmethod
    def load_albums_photos(dat):
        albums = wb_mg_doc.WeiboAlbums.objects(
            __raw__={'uid': dat['uid']}
        )
        dat = []
        for alb in albums:
            dat.append(alb._data)
        return dat

    @staticmethod
    def update_user_info(dat):
        wb_mg_doc.user_update(dat)
        log.debug('update person info done!!!')

    def show_user_info(self, dat):
        person_details = ''
        self.cat_net_img(dat['person_pic'])
        keys = list(dat.keys())
        for k in sorted(keys):
            person_details += '{}\n'.format(dat[k])
        helper.color_print(person_details)

    def follow(self, userinfo):
        """
            1. 关注
            2. 分组
        :return:
        :rtype:
        """
        follow_data = {
            'uid': userinfo.get('uid'),
            'refer_sort': 'followlist',  # 必备参数
        }
        res = self.sess.post(M['do_follow'] + '&__rnd={}'.format(helper.unixtime(True)),
                             data=urlencode(follow_data),
                             headers=self.json_header)
        # print(res.url, follow_data)
        # print(res.status_code)
        # print(res.json())
        return res

    def unfollow(self, userinfo):
        form = {
            'uid': userinfo.get('uid')
        }
        res = self.sess.post(M['undo_follow'], data=form, headers=self.json_header)
        # print(res.url, form)
        # print(res.status_code)
        res = res.json()
        if res.get('code') == '100000':
            print('取消关注 <{}> 成功!'.format(userinfo.get('name')))
        else:
            print('取消关注 <{}> 失败: {}'.format(userinfo.get('name'), res))

    def unfollow_list(self, userinfo):
        sns = click.prompt('输入其他账号编号, 使用 , 分隔多个')
        sns = sns.split(',')
        for sn in sns:
            msg = self.cached_users_followed[int(sn) - 1].get('name')
            val = click.confirm('确定删除 {}'.format(msg), default=True)
            if val:
                self.unfollow(self.cached_users_followed[int(sn) - 1])

    def show_user_followed(self, user_info):
        select_user = {}
        c = ''
        while True:
            # 如果是 b/B, 则使用上次历史数据
            if c in ['n', 'N'] or not self.cached_users_followed:
                self.cached_users_followed_index += 1
                self.cached_users_followed = self._show_user_followed(user_info, self.cached_users_followed_index)
            if c in ['p', 'P'] or not self.cached_users_followed:
                if self.cached_users_followed_index <= 1:
                    log.warn('already the first page.')
                else:
                    self.cached_users_followed_index -= 1
                    self.cached_users_followed = self._show_user_followed(user_info, self.cached_users_followed_index)

            c = self.choose_user(self.cached_users_followed)

            if c in ['b', 'B']:
                return 'b'

            if isinstance(c, dict):
                select_user = c
            elif isinstance(c, str):
                continue

            actions = [
                {
                    'action': 'show_user_details',
                    'txt': '查看详情',
                },
                {
                    'action': 'follow',
                    'txt': '关注',
                },
                {
                    'action': 'unfollow',
                    'txt': '取消关注',
                }
            ]

            while True:
                c = helper.num_choice(
                    [x.get('txt') for x in actions],
                    valid_keys='b,B')
                if c in range(len(actions)):
                    print('{} > {}'.format(actions[c].get('txt'), select_user.get('name', '')))
                    getattr(self, actions[c].get('action'))(select_user)
                    continue
                return 'b'

    def _show_user_followed(self, user_info, page_index=1):
        """
            用户的关注

        :return:
        :rtype:
        """
        params = {
            't': 1,
            'cfs': ''
        }

        # 默认使用自己的信息
        _from_id = self.personal_info['domain'] + user_info['uid']
        follow_url = M['get_my_follow']
        follow_id = '"ns":"pl.relation.myFollow.index"'

        # 如果 uid 不同, 则为查看其他账号的关注列表
        if self.personal_info['uid'] != user_info['uid']:
            follow_id = '"ns":"pl.content.followTab.index"'
            params['page'] = page_index
            follow_url = M['get_follow']
        else:
            if self.domid:
                params['{}_page'.format(self.domid)] = page_index

        user_raw = self.do_get_weibo_stk_to_html(
            follow_url.format(_from_id),
            params=params,
            patten_id=follow_id
        )

        def action_to_dict(plain):
            dat = {}
            if not plain:
                return dat

            acts = plain.split('&')

            for act in acts:
                k, v = act.split('=')
                if k and v:
                    dat[k] = v
            return dat

        def my_followed():
            """
            <img alt="主播佳期" class="W_face_radius" height="50"
            src="//tva4.sinaimg.cn/crop.3.0.506.506.50/9549f643jw8f9dvpn6kn3j20e80e2gm7.jpg"
            title="主播佳期" usercard="id=2504652355" width="50"/>

            action-data="uid=1915268965
            &profile_image_url=http://tvax1.sinaimg.cn/crop.0.0.1242.1242.50/7228af65ly8fmc4jx2rwij20yi0yi419.jpg
            &gid=0&gname=未分组&screen_name=霹雳无敌李三娘&sex=f"
            """
            member_box = user_raw.find('div', 'member_box')
            members_raw = member_box.find_all('li', 'member_li S_bg1')
            members_ = []

            for li in members_raw:
                followed = action_to_dict(li.get('action-data'))
                img_src = self.use_big_head(followed.get('profile_image_url'))
                followed_from = li.find('div', 'info_from S_txt2').a.text
                approve = li.find('i', 'W_icon')
                if approve:
                    approve = approve.get('title')
                else:
                    approve = ''
                d = {
                    'person_pic': img_src,
                    'name': followed.get('screen_name', ''),
                    'uid': followed.get('uid', ''),
                    'sex': followed.get('sex'),
                    'followed_from': helper.multi_replace(followed_from, '\r|\n|\t'),
                    'approve': helper.multi_replace(approve, '微博|认证')
                }
                members_.append(d)
            return members_

        def user_followed():
            """
                action-data="uid=5943836571&fnick=叫什么不一定&sex=f"
                //tvax1.sinaimg.cn/crop.0.0.512.512.50/006ufJpNly8fme6z2nhfmj30e80e8mxi.jpg

            :return:
            :rtype:
            """
            follow_list = user_raw.find('ul', 'follow_list')
            members_ = []
            for li in follow_list.find_all('li', 'follow_item S_line2'):
                img_src = self.use_big_head(li.find('img').get('src'))

                info = li.get('action-data')
                followed = action_to_dict(info)
                d = {
                    'name': followed.get('fnick', ''),
                    'uid': followed.get('uid', ''),
                    'sex': followed.get('sex'),
                    'person_pic': img_src,
                }
                members_.append(d)

            return members_

        if self.personal_info['uid'] != user_info['uid']:
            members = user_followed()
        else:
            members = my_followed()

        return members

    def show_user_fans(self, user):
        print('Fans')

    def show_user_details(self, userinfo):
        user_details = self.do_search_user(userinfo)[0]
        plain_info = ''
        keys = list(user_details.keys())
        for k in sorted(keys):
            plain_info += '{}\n'.format(user_details[k])

        self.cat_net_img(user_details.get('person_pic'))
        helper.color_print(plain_info)

    def choose_user(self, users_in, auto_select=False):
        def __show(user):
            sex_ = ''
            if user.get('sex'):
                sex_ = ' ♂ ' if user.get('sex') == 'm' else ' ♀ '

            _display = '{:<16}'.format(user['uid'] + sex_)
            _display += '{}'.format(user['name'])

            # for x in ['approve', 'person_num']:
            if user.get('approve'):
                _display += '「{}」'.format(user.get('approve'))

            if user.get('person_num'):
                _display += '<{}>'.format(user.get('person_num'))

            if user.get('followed_from'):
                _display += '『{}』'.format(user.get('followed_from'))
            return _display

        if not auto_select:
            c = helper.num_choice(
                [
                    __show(x)
                    for x in users_in
                ],
                valid_keys='n,N,p,P',
                separator=['*' * 64],
            )
        else:
            c = 0

        if c in range(len(users_in)):
            user_details = users_in[c]
            plain_info = ''
            keys = list(user_details.keys())
            for k in sorted(keys):
                plain_info += '{}\n'.format(user_details[k])

            self.cat_net_img(user_details.get('person_pic'))
            y = helper.yn_choice(plain_info, separator=['*' * 64])
            if y:
                return user_details
            else:
                return 'b'
        else:
            return c

    def click_fn_search(self, fn, username, auto_select=False):
        c = 'n'
        page_index = 0

        users = []
        while c in ['n', 'N', 'b', 'B']:
            # 如果是 b/B, 则使用上次历史数据
            if c not in ['b', 'B']:
                page_index += 1
                users = getattr(self, fn)(username, page_index)

            c = self.choose_user(users, auto_select=auto_select)

        return c

    def click_fn_user_actions(self, user_details):
        if not user_details:
            return

        actions = [
            'show_user_info',
            'show_user_followed',
            'show_user_fans',
            'update_user_info',
            'update_albums',
            'load_albums_photos',
            'follow',
            'unfollow',
            'unfollow_list',
        ]
        c = 'b'
        running = [x for x in range(len(actions))]
        running += ['b', 'B']
        while c in running:
            c = helper.num_choice(
                actions,
                default='2')
            if c in range(len(actions)):
                if actions[c] == 'load_albums_photos':
                    break
                getattr(self, actions[c])(user_details)

    def click_fn_update_photos(self, user_details, init):
        c = 'b'
        albums = self.load_albums_photos(user_details)
        while c in ['b', 'B']:
            c = helper.num_choice(
                [
                    '{:<32}{}({})'.format(x['album_id'], x['caption'], x['count']['photos'])
                    for x in albums
                ]
            )
            if c in ['b', 'B']:
                continue

            self.update_photos(albums[c], init_photos=init)
            break


click_hint = '{}\nUSAGE: <cmd> {}'


@click.command()
@click.option('--search', '-s',
              help=click_hint.format('从新浪直接查询', '-s <name>'))
@click.option('--name', '-n',
              help=click_hint.format('从本地mongo查询', '-n <name>'))
@click.option('--login', '-lg',
              is_flag=True,
              help=click_hint.format('手动登陆', ' -lg'))
@click.option('--init', '-i',
              is_flag=True,
              help=click_hint.format('初始化账号专辑照片信息, 否则只更新', ' -i'))
@click.option('--update_personal_info', '-update',
              is_flag=True,
              help=click_hint.format('更新个人信息', ' -update'))
@click.option('--test', '-t',
              is_flag=True,
              help=click_hint.format('测试cookie是否可用', ' -t'))
@click.option('--skip_cache', '-sc',
              is_flag=True,
              help=click_hint.format('不使用照片缓存', ' -sc'))
@click.option('--big_head', '-big',
              is_flag=True,
              help=click_hint.format('显示原始大图', ' -big'))
@click.option('--img_height', '-h',
              type=int,
              help=click_hint.format('iterm2 终端显示照片占用的行数', '-h <num>'))
@click.option('--img_cache_dir', '-cache',
              help=click_hint.format('终端显示照片缓存目录', '-cache <dir>'))
@click.option('--log_level', '-log',
              type=int,
              help=click_hint.format(
                  '终端显示log级别 1-debug/2-info/3-warn/4-error'
                  , '-log <num>'))
def run(search, login, name,
        big_head, img_cache_dir, skip_cache,
        img_height, log_level,
        test, init, update_personal_info,
        ):
    img_height = img_height or cfg.get('weibo.img_height', 3)
    log_level = log_level or cfg.get('weibo.log_level', 1)
    img_cache_dir = img_cache_dir or cfg.get('weibo.img_cache_dir', '/tmp/weibo')

    big_head = big_head or cfg.get('weibo.big_head', False)
    skip_cache = skip_cache or cfg.get('weibo.skip_cache', False)

    wb = Wb(big_head=big_head, img_cache_dir=img_cache_dir, img_height=img_height, use_cache=not skip_cache)
    user_details = {}
    logzero.loglevel(log_level * 10)

    if login:
        username = click.prompt('username', type=str)
        password = click.prompt('password', type=str, hide_input=True)
        wb.login(username, password)
        abc.force_quit()

    # 加载 cookies
    wb.sess.cookies = wb.load_cookies()
    wb.who_am_i()

    if not wb.sess.cookies:
        log.warn('no cookie found!, login first!!!')
        abc.force_quit()

    # 测试 cookie 是否可用
    if test:
        wb.is_cookie_ok()
        abc.force_quit()

    # 由账号名查询相关信息
    if search:
        user_details = wb.click_fn_search(
            'do_search_user',
            search,
        )

    # 查询本地数据库数据
    if name:
        user_details = wb.click_fn_search(
            'load_user_info',
            name,
        )

    if not name and not search:
        if update_personal_info:
            wb.update_personal_info()
        user_details = wb.click_fn_search(
            'load_user_info',
            wb.personal_info.get('nick'),
            auto_select=True,
        )

    if user_details:
        # 执行用户功能操作
        wb.click_fn_user_actions(user_details)
        # 更新用户照片到本地数据库中
        wb.click_fn_update_photos(user_details, init)


if __name__ == '__main__':
    run()
