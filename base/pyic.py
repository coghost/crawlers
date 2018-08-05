# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '2018/7/11 6:16 PM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''

import os
import sys
import random
from faker import Faker

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)


def m9():
    m = ['{}*{}={}'.format(j, i, j * i) for i in range(1, 10) for j in range(1, i + 1)]
    m = ['{}*{}={}{}'.format(j, i, j * i, '\r\n' if j == i else ' ') for i in range(1, 10) for j in
         range(1, i + 1)]
    print(''.join(m))
    print('\n'.join([' '.join(['%s*%s=%-2s' % (y, x, x * y) for y in range(1, x + 1)]) for x in range(1, 10)]))


def zip_dic():
    """
    names = ['Dickerson', 'Olsen', 'Johns', 'Martinez', 'Underwood']
    ages = 随机5个(18, 40)的值
    然后生成{name: age}字典
    :return:
    :rtype:
    """
    pass
    names = ['Dickerson', 'Olsen', 'Johns', 'Martinez', 'Underwood']
    ages = [random.randint(18, 40) for _ in range(5)]
    dat = dict(zip(names, ages))
    return dat

def pythonic_way(max_val=50):
    """
    依据max_val, 生成两个长度为10的由随机数组成的list_a, list_b
        - 如果 max_val 小于 100, 则生成 (0 ~ max_val*2) 的随机数组成 list
        - 如果 max_val 大于等于 100 但小于400, 生成 (0 ~ max_val) 的随机数组成 list
        - 如果 max_val 大于等于 400, 生成 (0 ~ max_val除以4) 的随机数组成 list

    list_a, list_b 分别取一个数, 查找和小于 max_val 的所有值组合
    组合要求:
        - 去重
        - 按(x, y)中的 y值升序, 然后x升序 排列

    :return: [(x1, y1), (x2, y2), ...]
    :rtype:
    """
    _min = 0
    l = 4
    # 三目表达式
    max_val = max_val * 2 if max_val < 100 else max_val if 100 <= max_val < 400 else max_val // 4
    # 推导式 写法
    a = [random.randint(_min, max_val) for _ in range(l)]
    b = [random.randint(_min, max_val) for _ in range(l)]
    # step1. < max_val
    un = [(x, y) for x in a for y in b if x + y < max_val]
    # 去重
    un = list(set(un))
    # 排序
    un = sorted(un, key=lambda x: (x[1], x[0]))

    return un


def b_search(val, arr):
    l, h = 0, len(arr) - 1
    while l <= h:
        m = (l + h) // 2
        # print(l, h, m)
        if val == arr[m]:
            return m
        elif val < arr[m]:
            h = m - 1
        elif val > arr[m]:
            l = m + 1

class Solution:
    def numMatchingSubseq(self, S, words):
        def check(s, i):
            for c in s:
                i = S.find(c, i) + 1
                if not i: return False
            return True

        return sum((check(word, 0) for word in words))


def run():
    # m9()
    fake = Faker()
    names = []
    for i in range(5):
        names.append(fake.name().split(' ')[1])
    print(names)


if __name__ == '__main__':
    run()
