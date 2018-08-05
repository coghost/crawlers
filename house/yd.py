# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '2018/7/2 10:41 AM'
__description__ = '''
北京信息科技大学: http://zhaosheng.bistu.edu.cn/front/zs/queryMark.jspa
    
'''

import os
import sys

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

from izen import helper


def cl2num():
    # 562, 552, 558, 556, 559, 554
    y = [0, 1, 5, 8, 14, 17]
    x = [2, 6, 7, 8, 9, 10, 11, 12, 13]
    sc = [7, 9, 11, 12]
    cnt = helper.to_str(helper.read_file('bj.txt'))
    for i, l in enumerate(cnt.split('\n')):
        l = [x for x in l.split(' ') if x]
        if i not in y:
            continue

        v = l
        s = '{}, 最高:{}, 最低:{}, 平均:{}, 人数:{}, 分数差:{}'.format(
            v[2], v[7], v[9], v[11], v[6], int(v[11]) - int(v[12])
        )
        print(s)


def dif():
    a = [562, 552, 558, 556, 559, 554]
    m = 484

    d_ = [x - m for x in a]
    print(d_)


if __name__ == '__main__':
    cl2num()
    # dif()
