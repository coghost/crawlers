# -*- coding: utf-8 -*-

import os
import sys

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)


def test_1():
    """
    names = ['Dickerson', 'Olsen', 'Johns', 'Martinez', 'Underwood']
    ages = 随机5个(18, 40)的值
    然后生成{name: age}字典
    :return:
    :rtype:
    """
    pass


def test_2():
    """
    新建一个数组, 并获取第一个, 最后一个, 及中间所有元素
    例如: 数组 nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    :return: (0, [1, 2, 3, 4, 5, 6, 7, 8], 9)
    :rtype:
    """
    pass


def test_3():
    """
    简单的 乘法口诀输出, 输出乘法口诀

    实现一行代码输出

    :return:
    :rtype:
    """
    for i in range(1, 10):
        for j in range(1, i + 1):
            print('{}*{}={}'.format(j, i, j * i), end=' ')
        print()


"""pythonic"""


def test_4(max_val=50):
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
    pass


def choice_1(t):
    """
    使用生成器生成 fibonacci
    :param t:
    :type t:
    :return:
    :rtype:
    """


"""algorithm 1"""


def algo_1(plain='aaaabbbbbbccccaa'):
    """
    输入 值为 aaaabbbbbbccccaa
    返回 a4b6c4a2
    >>> algo_1()
    'a4b6c4a2'
    :param plain:
    :type plain:
    :return:
    :rtype:
    """
    pass


def algo_2(val):
    """
    二分查找
    arr = [2, 8, 31, 32, 35, 49, 58, 74, 83, 109, 118, 127, 139, 143, 143, 146, 160, 161, 174, 199]
    val = 83
    >>> algo_2(83)
    8
    >>> algo_2(183)
    None
    """
    pass


def run():
    pass


if __name__ == '__main__':
    run()
