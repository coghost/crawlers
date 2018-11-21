# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '24/11/2017 4:05 PM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
- 参考: http://selenium-python-docs-zh.readthedocs.io/zh_CN/latest/installation.html
- https://www.cnblogs.com/luxiaojun/p/6144748.html
- http://cuiqingcai.com/2599.html
'''

import os
import sys
import time

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import selenium
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logzero import logger as log

chrome_mac = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'


def init_chrome():
    options = webdriver.ChromeOptions()
    prefs = {
        # 'profile.default_content_setting_values': {
        #     'images': 2,
        #     'cookies': 2,
        #     'popups': 0,
        # },
        # 'profile.default_content_setting_values.notifications': 2,
        # 'profile.default_content_settings.cookies': 2,
        # 'profile.default_content_settings.popups': 0,
        # 'download.default_directory': '/tmp/'
    }
    if 1:
        options.add_argument(
            'user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) '
            'AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"')
    else:
        options.add_argument('user-agent="{}"'.format(chrome_mac))

    # options.add_experimental_option('prefs', prefs)
    return webdriver.Chrome(chrome_options=options)


def ctfile_by_chrome(url):
    """
        城通网盘

    :param url:
    :return:
    """
    options = webdriver.ChromeOptions()
    prefs = {
        # 'profile.default_content_setting_values': {
        #     'images': 2,
        #     'cookies': 2,
        #     'popups': 0,
        # },
        # 'profile.default_content_setting_values.notifications': 2,
        # 'profile.default_content_settings.cookies': 2,
        # 'profile.default_content_settings.popups': 0,
        'download.default_directory': '/tmp/'
    }
    # options.add_argument(
    #     'user-agent="Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) '
    #     'AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"')

    options.add_argument('user-agent="{}"'.format(chrome_mac))

    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(chrome_options=options)
    driver.get(url)
    driver.find_element_by_id('free_down_link').send_keys(Keys.PAGE_DOWN)
    time.sleep(0.1)
    driver.find_element_by_id('free_down_link').click()
    driver.find_element_by_id('free_down_link').send_keys(Keys.PAGE_DOWN)
    time.sleep(0.1)
    driver.find_element_by_id('free_down_link').click()
    input('press any key to cancel download... ')
    driver.quit()


def fmt_cookie(url='https://pan.baidu.com'):
    ab = init_chrome()
    ab.get(url)
    cks = {}
    for ck in ab.get_cookies():
        cks[ck['name']] = ck['value']
    return cks


def baidu_pan_by_chrome(url='', pwd=''):
    """
        百度网盘
    :param url:
    :param pwd:
    :return:
    """
    ab = init_chrome()

    # 百度网盘下载提取页面需要有 cookie
    ab.get(url)
    cks = []
    for ck in ab.get_cookies():
        cks.append({
            'name': ck['name'],
            'value': ck['value'],
        })

    for ck in cks:
        ab.add_cookie(ck)

    ab.get(url)
    # 检查文件是否存在
    try:
        err_msg = ab.find_element_by_id('share_nofound_des')
        if err_msg:
            log.error(err_msg.text)
            ab.quit()
            return
    except NoSuchElementException as _:
        pass

    ab.find_element_by_tag_name('input').send_keys(pwd)
    time.sleep(0.1)
    ab.find_element_by_tag_name('input').send_keys(Keys.ENTER)
    time.sleep(0.1)
    ab.find_element_by_id('getfileBtn').click()
    wait = WebDriverWait(ab, 5)
    ele = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'slide-show-right')))

    btn_raw = ele.find_elements_by_class_name('g-button')
    for btn in btn_raw:
        if btn.text.find('下载') != -1:
            btn.send_keys(Keys.ENTER)
            break
    input('press any key to cancel download and exit... ')
    ab.quit()


def by_phantomjs():
    dcap = dict(DesiredCapabilities.PHANTOMJS)  # 设置userAgent
    dcap["phantomjs.page.settings.userAgent"] = (
        'Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, '
        'like Gecko) Chrome/62.0.3202.94 Mobile Safari/537.36')
    driver = webdriver.PhantomJS(desired_capabilities=dcap)
    driver.get("https://sdifen.ctfile.com/fs/DrL172779334")
    driver.find_element_by_tag_name('button').submit()
    driver.save_screenshot('1.png')
    # print(driver.page_source)
    # driver.find_element_by_tag_name('button').submit()
    driver.find_element_by_id('local_free').click()
    print(driver.page_source)
    driver.save_screenshot('2.png')
    # driver.close()


if __name__ == '__main__':
    baidu_pan_by_chrome('https://pan.baidu.com/s/1sk906Pf', 'wxgr')
    # by_android()
    # uri = "https://sdifen.ctfile.com/fs/DrL172779334"
    # ctfile_by_chrome(uri)
    # by_firefox()
    # by_phantomjs()
