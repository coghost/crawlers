# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '05/12/2017 4:29 PM'
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

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from logzero import logger as log


class PhantomPy(object):
    def __init__(self):
        dcap = dict(DesiredCapabilities.PHANTOMJS)  # 设置userAgent
        dcap["phantomjs.page.settings.userAgent"] = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0")

        self.driver = webdriver.PhantomJS(desired_capabilities=dcap)

    def do_get(self, url):
        self.driver.get(url)
        return self.driver.page_source
