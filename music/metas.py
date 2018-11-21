# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '11/20 10:25'
__description__ = '''
'''

import os
import sys

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

from mutagen.id3 import ID3, TIT2

if __name__ == '__main__':
    pass
