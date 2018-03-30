#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '07/12/2017 2:20 PM'
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
from base import dbstore
from proxies import mg_doc

M = {
    'free_index': 'http://www.kuaidaili.com/free/inha/{}/',
    'ops_index': 'http://www.kuaidaili.com/ops/proxylist/{}/',
    'refer': 'http://www.kuaidaili.com/ops',
}


class Kuai(Crawl):
    def __init__(self,
                 refer=M.get('refer', ''),
                 parser='html5lib',
                 ):
        Crawl.__init__(self, refer,
                       parser=parser)
        self.end_date = ''

    def get_page(self, url_in=M['free_index'], page_index=1, id_='list'):
        url = url_in.format(page_index)
        _raw = self.do_get({
            'url': url,
        })
        if not _raw:
            return
        raw = self.bs4markup(_raw)
        freelist = raw.find('div', id=id_)

        table = freelist.find('table')
        return self.take_proxies(table=table)

    @staticmethod
    def take_proxies(table):
        """ 解析 table 数据生成 dict 结构

        :param table:
        :return:
        """
        # keys = 'ip,port,location,anonymity,protocol,speed,conn_time,alive,checked'.split(',')
        keys = 'ip,port,anonymity,protocol,method,location,speed,checked'.split(',')
        trs = table.find('tbody').find_all('tr')

        dat = []
        for tr in trs[1:]:
            try:
                d = {}
                tds = tr.find_all('td')

                for i, td in enumerate(tds):
                    txt = td.text.replace('\n', '').rstrip().lstrip()
                    d[keys[i]] = txt

                dat.append(d)
            except AttributeError as _:
                log.debug('{}: {}'.format(tr, _))

        return dat

    def get_ops_pages(self):
        """
            total 10 pages

        :return:
        """
        dat = []
        for i in tqdm(range(10), ascii=True):
            i += 1
            dat += self.get_page(M['ops_index'], i, id_='freelist')
            time.sleep(abc.randint(5, 10))

        self.save_to_db(dat, 'kdl.ops.proxies')
        return dat

    def get_free_pages(self):
        for i in tqdm(range(1963), ascii=True):
            i += 1
            if i <= int(cfg.get('kdl.last_index', 0)):
                continue
            log.debug('START@({})'.format(i))
            dat = self.get_page(M['free_index'], i)
            if dat:
                self.save_to_db(dat, 'kdl.free.proxies')
                abc.update_cfg('kdl.last_index', i)

            time.sleep(abc.randint(5, 10))

    def cache_data(self):
        d = [{
            'ip': '121.232.145.237',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 江苏省 镇江市 电信',
            'speed': '2秒',
            'checked': '9分钟前'
        }, {
            'ip': '111.155.124.74',
            'port': '8123',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 陕西省  铁通',
            'speed': '1秒',
            'checked': '12分钟前'
        }, {
            'ip': '202.98.19.149',
            'port': '80',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 吉林省 长春市 联通',
            'speed': '0.7秒',
            'checked': '15分钟前'
        }, {
            'ip': '121.232.145.115',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 江苏省 镇江市 电信',
            'speed': '1秒',
            'checked': '18分钟前'
        }, {
            'ip': '122.96.59.107',
            'port': '80',
            'anonymity': '匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '江苏省南京市 联通',
            'speed': '3秒',
            'checked': '21分钟前'
        }, {
            'ip': '112.25.35.76',
            'port': '80',
            'anonymity': '匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 江苏省 南京市 移动',
            'speed': '2秒',
            'checked': '24分钟前'
        }, {
            'ip': '121.31.102.240',
            'port': '8123',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '广西壮族自治区防城港市  联通',
            'speed': '2秒',
            'checked': '27分钟前'
        }, {
            'ip': '121.232.146.145',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 江苏省 镇江市 电信',
            'speed': '0.6秒',
            'checked': '30分钟前'
        }, {
            'ip': '121.232.145.199',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 江苏省 镇江市 电信',
            'speed': '0.4秒',
            'checked': '33分钟前'
        }, {
            'ip': '39.155.169.70',
            'port': '80',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 北京市 北京市 移动',
            'speed': '2秒',
            'checked': '36分钟前'
        }, {
            'ip': '223.241.116.6',
            'port': '8010',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 安徽省 芜湖市 电信',
            'speed': '2秒',
            'checked': '40分钟前'
        }, {
            'ip': '218.3.75.154',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 江苏省 镇江市 电信',
            'speed': '0.6秒',
            'checked': '42分钟前'
        }, {
            'ip': '120.25.253.234',
            'port': '8118',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 广东省 深圳市 阿里云',
            'speed': '1.0秒',
            'checked': '45分钟前'
        }, {
            'ip': '121.232.148.183',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 江苏省 镇江市 电信',
            'speed': '3秒',
            'checked': '49分钟前'
        }, {
            'ip': '122.96.59.107',
            'port': '843',
            'anonymity': '匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '江苏省南京市 联通',
            'speed': '2秒',
            'checked': '51分钟前'
        }, {
            'ip': '59.45.75.10',
            'port': '80',
            'anonymity': '匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 辽宁省 本溪市 电信',
            'speed': '3秒',
            'checked': '54分钟前'
        }, {
            'ip': '115.154.191.26',
            'port': '8089',
            'anonymity': '匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 陕西省 西安市 教育网',
            'speed': '2秒',
            'checked': '57分钟前'
        }, {
            'ip': '124.42.7.103',
            'port': '80',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 北京市 北京市 光环新网',
            'speed': '3秒',
            'checked': '1小时前'
        }, {
            'ip': '223.241.78.103',
            'port': '8010',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 安徽省 芜湖市 电信',
            'speed': '0.9秒',
            'checked': '1小时前'
        }, {
            'ip': '111.155.116.215',
            'port': '8123',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 陕西省  铁通',
            'speed': '2秒',
            'checked': '1小时前'
        }, {
            'ip': '218.14.121.237',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '广东省惠州市 电信',
            'speed': '1秒',
            'checked': '1小时前'
        }, {
            'ip': '223.241.118.171',
            'port': '8010',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 安徽省 芜湖市 电信',
            'speed': '3秒',
            'checked': '1小时前'
        }, {
            'ip': '121.35.243.157',
            'port': '8080',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 广东省 深圳市 电信',
            'speed': '3秒',
            'checked': '1小时前'
        }, {
            'ip': '60.191.168.181',
            'port': '3128',
            'anonymity': '透明',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '浙江省台州市  电信',
            'speed': '3秒',
            'checked': '1小时前'
        }, {
            'ip': '218.17.30.29',
            'port': '8888',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 广东省 深圳市 电信',
            'speed': '3秒',
            'checked': '1小时前'
        }, {
            'ip': '183.26.235.69',
            'port': '8118',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 广东省 佛山市 电信',
            'speed': '1秒',
            'checked': '1小时前'
        }, {
            'ip': '119.5.0.16',
            'port': '22',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 四川省 南充市 联通',
            'speed': '2秒',
            'checked': '1小时前'
        }, {
            'ip': '111.74.56.243',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '江西省赣州市 电信',
            'speed': '2秒',
            'checked': '1小时前'
        }, {
            'ip': '121.40.108.76',
            'port': '80',
            'anonymity': '匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 浙江省 杭州市 阿里云',
            'speed': '3秒',
            'checked': '1小时前'
        }, {
            'ip': '182.139.160.86',
            'port': '9797',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 四川省 成都市 电信',
            'speed': '3秒',
            'checked': '1小时前'
        }, {
            'ip': '121.232.147.163',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 江苏省 镇江市 电信',
            'speed': '0.7秒',
            'checked': '1小时前'
        }, {
            'ip': '27.46.74.27',
            'port': '9999',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 广东省 深圳市 联通',
            'speed': '3秒',
            'checked': '1小时前'
        }, {
            'ip': '162.105.86.156',
            'port': '8123',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 北京市 北京市 教育网',
            'speed': '3秒',
            'checked': '1小时前'
        }, {
            'ip': '124.88.84.154',
            'port': '8080',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 新疆维吾尔自治区 乌鲁木齐市 联通',
            'speed': '0.7秒',
            'checked': '1小时前'
        }, {
            'ip': '119.130.115.226',
            'port': '808',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 广东省 广州市 电信',
            'speed': '2秒',
            'checked': '1小时前'
        }, {
            'ip': '110.72.192.103',
            'port': '8123',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '广西壮族自治区南宁市  联通',
            'speed': '3秒',
            'checked': '2小时前'
        }, {
            'ip': '122.96.59.99',
            'port': '843',
            'anonymity': '匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '江苏省南京市 联通',
            'speed': '1秒',
            'checked': '2小时前'
        }, {
            'ip': '112.95.205.59',
            'port': '8888',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '广东省深圳市  联通',
            'speed': '3秒',
            'checked': '2小时前'
        }, {
            'ip': '222.217.19.248',
            'port': '8080',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '广西壮族自治区柳州市  电信',
            'speed': '0.5秒',
            'checked': '2小时前'
        }, {
            'ip': '121.232.144.214',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 江苏省 镇江市 电信',
            'speed': '3秒',
            'checked': '2小时前'
        }, {
            'ip': '223.96.95.229',
            'port': '3128',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 山东省 淄博市 移动',
            'speed': '1秒',
            'checked': '2小时前'
        }, {
            'ip': '115.46.89.112',
            'port': '8123',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '广西壮族自治区北海市  联通',
            'speed': '2秒',
            'checked': '2小时前'
        }, {
            'ip': '222.74.225.231',
            'port': '3128',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 内蒙古自治区 呼和浩特市 电信',
            'speed': '3秒',
            'checked': '2小时前'
        }, {
            'ip': '110.172.220.197',
            'port': '8080',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 北京市 北京市 联通',
            'speed': '3秒',
            'checked': '2小时前'
        }, {
            'ip': '119.5.0.27',
            'port': '22',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 四川省 南充市 联通',
            'speed': '3秒',
            'checked': '2小时前'
        }, {
            'ip': '120.26.51.101',
            'port': '8118',
            'anonymity': '匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 浙江省 杭州市 阿里云',
            'speed': '2秒',
            'checked': '2小时前'
        }, {
            'ip': '118.178.227.171',
            'port': '80',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 浙江省 杭州市 阿里云',
            'speed': '2秒',
            'checked': '2小时前'
        }, {
            'ip': '182.88.161.252',
            'port': '8123',
            'anonymity': '匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 广西壮族自治区 南宁市 联通',
            'speed': '0.6秒',
            'checked': '2小时前'
        }, {
            'ip': '118.119.168.172',
            'port': '9999',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 四川省 乐山市 电信',
            'speed': '1秒',
            'checked': '2小时前'
        }, {
            'ip': '202.109.207.126',
            'port': '8888',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 福建省 福州市 电信',
            'speed': '1秒',
            'checked': '2小时前'
        }, {
            'ip': '112.95.205.61',
            'port': '8888',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '广东省深圳市  联通',
            'speed': '1.0秒',
            'checked': '2小时前'
        }, {
            'ip': '121.232.148.146',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 江苏省 镇江市 电信',
            'speed': '0.8秒',
            'checked': '2小时前'
        }, {
            'ip': '111.47.17.106',
            'port': '8123',
            'anonymity': '匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 湖北省  移动',
            'speed': '2秒',
            'checked': '2小时前'
        }, {
            'ip': '218.14.121.229',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '广东省惠州市 电信',
            'speed': '2秒',
            'checked': '3小时前'
        }, {
            'ip': '117.78.50.121',
            'port': '8118',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 北京市 北京市 联通',
            'speed': '0.4秒',
            'checked': '3小时前'
        }, {
            'ip': '121.232.147.145',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 江苏省 镇江市 电信',
            'speed': '0.3秒',
            'checked': '3小时前'
        }, {
            'ip': '106.3.240.209',
            'port': '8080',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 北京市 北京市',
            'speed': '1秒',
            'checked': '3小时前'
        }, {
            'ip': '180.118.33.104',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 江苏省 镇江市 电信',
            'speed': '2秒',
            'checked': '3小时前'
        }, {
            'ip': '119.254.88.53',
            'port': '8080',
            'anonymity': '匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 北京市 北京市 华瑞信通',
            'speed': '2秒',
            'checked': '3小时前'
        }, {
            'ip': '121.10.1.182',
            'port': '8080',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 广东省 东莞市 电信',
            'speed': '1秒',
            'checked': '3小时前'
        }, {
            'ip': '180.118.247.244',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 江苏省 镇江市 电信',
            'speed': '2秒',
            'checked': '3小时前'
        }, {
            'ip': '219.150.189.212',
            'port': '9999',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 河南省 洛阳市 电信',
            'speed': '1秒',
            'checked': '3小时前'
        }, {
            'ip': '121.232.145.128',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 江苏省 镇江市 电信',
            'speed': '3秒',
            'checked': '3小时前'
        }, {
            'ip': '223.241.118.84',
            'port': '8010',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 安徽省 芜湖市 电信',
            'speed': '0.9秒',
            'checked': '3小时前'
        }, {
            'ip': '60.214.154.2',
            'port': '53281',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 山东省 枣庄市 联通',
            'speed': '1秒',
            'checked': '3小时前'
        }, {
            'ip': '114.67.229.117',
            'port': '8118',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 北京市 北京市 电信',
            'speed': '3秒',
            'checked': '3小时前'
        }, {
            'ip': '221.237.154.58',
            'port': '9797',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '四川省成都市  电信',
            'speed': '1秒',
            'checked': '3小时前'
        }, {
            'ip': '118.193.107.192',
            'port': '80',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 北京市 北京市 电信',
            'speed': '3秒',
            'checked': '3小时前'
        }, {
            'ip': '223.223.187.195',
            'port': '80',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 北京市 北京市',
            'speed': '3秒',
            'checked': '3小时前'
        }, {
            'ip': '221.214.110.130',
            'port': '8080',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 山东省 济南市 联通',
            'speed': '1秒',
            'checked': '3小时前'
        }, {
            'ip': '125.67.73.123',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 四川省 遂宁市 电信',
            'speed': '3秒',
            'checked': '3小时前'
        }, {
            'ip': '119.23.63.152',
            'port': '8118',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 广东省 深圳市 阿里云',
            'speed': '1秒',
            'checked': '4小时前'
        }, {
            'ip': '182.88.167.199',
            'port': '8123',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '广西壮族自治区南宁市  联通',
            'speed': '1秒',
            'checked': '4小时前'
        }, {
            'ip': '223.223.203.30',
            'port': '8080',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 北京市 北京市 皓宽网络',
            'speed': '2秒',
            'checked': '4小时前'
        }, {
            'ip': '182.148.123.137',
            'port': '8080',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 四川省 成都市 电信',
            'speed': '2秒',
            'checked': '4小时前'
        }, {
            'ip': '58.222.181.139',
            'port': '3128',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 江苏省 泰州市 电信',
            'speed': '1秒',
            'checked': '4小时前'
        }, {
            'ip': '58.56.90.202',
            'port': '53281',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 山东省 济南市 电信',
            'speed': '0.4秒',
            'checked': '4小时前'
        }, {
            'ip': '119.5.0.37',
            'port': '22',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 四川省 南充市 联通',
            'speed': '3秒',
            'checked': '4小时前'
        }, {
            'ip': '115.46.75.221',
            'port': '8123',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 广西壮族自治区 北海市 联通',
            'speed': '1秒',
            'checked': '4小时前'
        }, {
            'ip': '119.145.203.58',
            'port': '80',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 广东省 河源市 电信',
            'speed': '2秒',
            'checked': '4小时前'
        }, {
            'ip': '223.241.78.99',
            'port': '8010',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 安徽省 芜湖市 电信',
            'speed': '3秒',
            'checked': '4小时前'
        }, {
            'ip': '113.209.31.29',
            'port': '8118',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 北京市 北京市 电信',
            'speed': '1秒',
            'checked': '4小时前'
        }, {
            'ip': '159.226.103.235',
            'port': '8080',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 江苏省 南京市 科技网',
            'speed': '2秒',
            'checked': '4小时前'
        }, {
            'ip': '121.232.145.204',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 江苏省 镇江市 电信',
            'speed': '2秒',
            'checked': '4小时前'
        }, {
            'ip': '223.241.117.42',
            'port': '8010',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 安徽省 芜湖市 电信',
            'speed': '0.3秒',
            'checked': '4小时前'
        }, {
            'ip': '116.23.95.90',
            'port': '9999',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '广东省广州市  电信',
            'speed': '0.9秒',
            'checked': '4小时前'
        }, {
            'ip': '122.96.59.102',
            'port': '83',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '江苏省南京市 联通',
            'speed': '2秒',
            'checked': '4小时前'
        }, {
            'ip': '121.232.144.17',
            'port': '9000',
            'anonymity': '高匿名',
            'protocol': 'HTTP',
            'method': 'GET, POST',
            'location': '中国 江苏省 镇江市 电信',
            'speed': '3秒',
            'checked': '4小时前'
        }, {
            'ip': '58.56.149.198',
            'port': '53281',
            'anonymity': '高匿名',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 山东省 青岛市 电信',
            'speed': '3秒',
            'checked': '4小时前'
        }, {
            'ip': '120.204.85.29',
            'port': '3128',
            'anonymity': '透明',
            'protocol': 'HTTP, HTTPS',
            'method': 'GET, POST',
            'location': '中国 上海市 上海市 移动',
            'speed': '3秒',
            'checked': '5小时前'
        }]
        return d

    def save_to_db(self, dat, tb):
        dbstore.batch_write(dat, tb)


def run():
    k = Kuai()
    # d = k.cache_data()
    # kdl_l = dbstore.rds.List(key='kdl.ops.proxies')
    # kdl_l += d
    # k.save_to_db()
    # dat = k.get_page(url_in=M['free_index'], page_index=1)
    # dat = k.get_ops_pages()
    k.get_free_pages()
    # print(dat)


if __name__ == '__main__':
    run()
