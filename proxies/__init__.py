# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '06/12/2017 10:26 AM'
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

if __name__ == '__main__':
    pass
