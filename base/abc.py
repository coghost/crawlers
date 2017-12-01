# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '26/10/2017 9:56 AM'
__description__ = '''
    ☰
  ☱   ☴
☲   ☯   ☵
  ☳   ☶
    ☷
'''

import os
import sys
import logging
import subprocess
import threading
from functools import wraps

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(app_root)
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding('utf-8')

import profig
import click
from clint import textui

import logzero
from logzero import logger as log
from base import icons

from bs4 import BeautifulSoup


class Conf(object):
    """运行所需要的配置文件
    """

    def __init__(self, pth=None):
        self.pth = pth if pth else os.path.join(app_root, 'base/.crawl.cnf')
        self.cfg = profig.Config(self.pth, encoding='utf-8')
        self.cfg.read()
        self.init_type()
        if not os.path.exists(os.path.expanduser(self.pth)):
            self.cfg.sync()
            raise SystemExit('config file path not exists: {}'.format(os.path.expanduser(self.pth)))

    def init_type(self):
        """通过手动方式, 指定类型, 如果配置文件有变动, 需要手动在这里添加"""
        _cfg = self.cfg
        _cfg.init('log.enabled', False, bool)  # 是否记录到文件
        _cfg.init('log.file_pth', '/tmp/crawl.log', str)
        _cfg.init('log.file_backups', 3, int)
        _cfg.init('log.file_size', 5, int)  # M
        _cfg.init('log.level', 10, int)  # d/i/w/e/c 10/20/30/40/50
        _cfg.init('log.symbol', '☰☷☳☴☵☲☶☱', str)  # 使用前5个字符

        _cfg.init('mzt.base_dir', '/tmp/mzt', str)

        _cfg.init('pjw.base_dir', '/tmp/pjw', str)

        _cfg.init('d4.base_dir', '/tmp/d4', str)
        _cfg.init('d4.tag_index', 0, int)

        _cfg.init('movie.base_dir', '/tmp/moview', str)

        _cfg.init('mg.host', '127.0.0.1', str)
        _cfg.init('mg.port', 27027, int)
        _cfg.init('mg.db', 'luoo', str)
        _cfg.init('mg.username', '', str)
        _cfg.init('mg.password', '', str)

        _cfg.sync()


class LFormatter(logzero.LogFormatter):
    """ 改写 logzero 的 LogFormatter
    - 移除 ``[]``, 支持自定义前导字符(任意长度, 但只取前5个字符),
    - 增加 ``critical`` 的颜色实现
    """
    DEFAULT_FORMAT = '%(color)s {}%(levelname)1.1s %(asctime)s ' \
                     '%(module)s:%(lineno)d {}%(end_color)s %(' \
                     'message)s'
    DEFAULT_DATE_FORMAT = '%y%m%d %H:%M:%S'
    DEFAULT_COLORS = {
        logging.DEBUG: logzero.ForegroundColors.CYAN,
        logging.INFO: logzero.ForegroundColors.GREEN,
        logging.WARNING: logzero.ForegroundColors.YELLOW,
        logging.ERROR: logzero.ForegroundColors.RED,
        logging.CRITICAL: logzero.ForegroundColors.MAGENTA,
    }

    def __init__(self, log_pre='♨✔⊙✘◈'):
        logzero.LogFormatter.__init__(self,
                                      datefmt=self.DEFAULT_DATE_FORMAT,
                                      colors=self.DEFAULT_COLORS
                                      )
        blank__ = '➵' * 5
        log_pre += blank__[len(log_pre):]  # 如果无, 或者长度小于5, 则使用 blank_ 自动补全5个字符
        self.CHAR_PRE = dict(zip(range(5), log_pre))

    def format(self, record):
        _char_pre = self.CHAR_PRE[record.levelno / 10 - 1] + ' '
        __fmt = self.DEFAULT_FORMAT
        __fmt = __fmt.format(_char_pre, '|')
        self._fmt = __fmt
        return logzero.LogFormatter.format(self, record)


cfg = Conf().cfg

# 检查日志配置, 是否写入文件
if cfg.get('log.enabled', False):
    logzero.logfile(
        cfg.get('log.file_pth', '/tmp/igt.log'),
        maxBytes=cfg.get('log.file_size', 5) * 1000000,
        backupCount=cfg.get('log.file_backups', 3),
        loglevel=cfg.get('log.level', 10),
    )

# bagua = '☼✔❄✖✄'
# bagua = '☰☷☳☴☵☲☶☱'  # 乾(天), 坤(地), 震(雷), 巽(xun, 风), 坎(水), 离(火), 艮(山), 兑(泽)
bagua = '🍺🍻♨️️😈☠'
formatter = LFormatter(bagua)
logzero.formatter(formatter)


def set_clipboard_data(data):
    p = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
    p.stdin.write(to_bytes(data))
    p.stdin.close()
    p.communicate()


def bs4markup(params=None):
    """
        **format the markup str to BeautifulSoup doc.**

    .. code:: python

        @bs4markup
        def fn():
            pass

    :rtype: BeautifulSoup
    :param params: ``{'parser': 'html5lib'}``
    :return:
    """
    params = params or {}

    def dec(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                rs = fn(*args, **kwargs)
                markup = BeautifulSoup(
                    rs,
                    params.get('parser', 'html5lib'),
                )
                if rs == markup.text:
                    return rs
                else:
                    return markup
            except TypeError as _:
                pass

        return wrapper

    return dec


def threads(bg=False, my_exception=TypeError):
    def dec(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if bg:
                try:
                    t = threading.Thread(target=fn, args=args)
                    t.daemon = True
                    t.start()
                    return t
                except my_exception as e:
                    print(e)
            else:
                return fn(*args, **kwargs)

        return wrapper

    return dec


def catch(do, my_exception=TypeError):
    """
    防止程序出现 exception后异常退出,
    但是这里的异常捕获机制仅仅是为了防止程序退出, 无法做相应处理
    可以支持有参数或者无参数模式

    -  ``do == True`` , 则启用捕获异常
    -  无参数也启用 try-catch

    .. code:: python

            @catch
            def fnc():
                pass

    -  在有可能出错的函数前添加, 不要在最外层添加,
    -  这个catch 会捕获从该函数开始的所有异常, 会隐藏下一级函数调用的错误.
    -  但是如果在内层的函数也有捕获方法, 则都会catch到异常.

    :param my_exception:
    :type my_exception:
    :param do:
    :type do:
    :return:
    :rtype:
    """
    if not callable(do):
        def dec(fn):
            @wraps(fn)
            def wrapper_(*args, **kwargs):
                if not do:
                    return fn(*args, **kwargs)

                try:
                    return fn(*args, **kwargs)
                except my_exception as e:
                    print("file-func({}({}):{}) : has err({})".format(
                        fn.__code__.co_filename.split('/')[-1],
                        fn.__code__.co_firstlineno,
                        fn.__name__, e))

            return wrapper_

        return dec

    @wraps(do)
    def wrapper(*args, **kwargs):
        try:
            return do(*args, **kwargs)
        except my_exception as e:
            print("file-func({}({}):{}) : has err({})".format(
                do.__code__.co_filename.split('/')[-1],
                do.__code__.co_firstlineno,
                do.__name__, e
            ))

    return wrapper


def update_cfg(key, val):
    cfg[key] = val
    cfg.sync()


def mkdir_p(pathin, is_dir=False):
    """
        分隔pathin, 并以此创建层级目录

    - ``is_dir == True``: 则将所有 ``/ 分隔`` 的pathin 当前文件夹
    - 否则, 将分隔的最后一个元素当做是文件处理

    >>> # 创建一个目录 /tmp/a/b/c
    >>> mkdir_p('/tmp/a/b/c/001.log')

    :param is_dir: ``是否目录``
    :type is_dir: bool
    :param pathin: ``待创建的目录或者文件路径``
    :type pathin: str
    """
    h, _ = os.path.split(pathin)
    if is_dir:
        h = pathin
    try:
        if not os.path.exists(h):
            os.makedirs(h)
    except FileExistsError as fe:
        pass
    except Exception as err:
        raise err


def write_abs_file(dat, pth, append=True):
    """
        将 ``dat`` 内容写入 绝对路径 ``pth`` 中

    :param append:
    :type append:
    :param dat:
    :type dat:
    :param pth:
    :type pth:
    :return:
    :rtype:
    """
    _d, _nm = os.path.split(pth)
    err = None
    if not os.path.exists(_d):
        os.makedirs(_d)
    try:
        mode = 'ab' if append else 'wb'

        with open(pth, mode) as _fp:
            _fp.write(dat)
    except Exception as _err:
        err = _err
    return err


def write_file(dat, pth):
    """
        写入 ``dat`` 内容到相对路径中

    :param dat:
    :type dat:
    :param pth:
    :type pth:
    :return:
    :rtype:
    """
    if hasattr(dat, 'encode'):
        dat = dat.encode()
    with open(pth, 'wb') as fp:
        fp.write(dat)


def read_file(pth):
    """
        读取文件, 并返回内容,
        如果读取失败,返回None

    :param pth:
    :type pth:
    :return:
    :rtype:
    """
    cont = None
    try:
        with open(u'' + pth, 'rb') as fp:
            cont = fp.read()
    except Exception as err:
        print(err)
    return cont


def save_img(dat, pth):
    if not dat:
        return
    write_file(dat, pth)


def clear_empty_file(pathin, extensions=None, do_clear=False):
    if not os.path.exists(pathin):
        log.debug('{} not exist'.format(pathin))
        return

    for root, dirs, files in os.walk(pathin):
        for f in files:
            ext = f.split('.')[-1]
            if extensions and ext not in extensions:
                # if '.jpg' not in f:
                continue
            _fpth = os.path.join(root, f)
            if not is_file_ok(_fpth):
                log.debug('rm file: {}/{}'.format(root, f.split('-')[1]))
                if do_clear:
                    os.remove(_fpth)


def is_file_ok(fpth):
    try:
        return os.path.getsize(fpth)
    except FileNotFoundError as _:
        return 0


def to_str(str_or_bytes, charset='utf-8'):
    """
    转换 dat 为 str
    :param str_or_bytes:
    :type str_or_bytes:
    :param charset:
    :type charset:
    :return:
    :rtype:
    """
    return str_or_bytes.decode(charset) if hasattr(str_or_bytes, 'decode') else str_or_bytes


def to_bytes(str_or_bytes):
    return str_or_bytes.encode() if hasattr(str_or_bytes, 'encode') else str_or_bytes


def get_sys_cmd_output(cmd):
    """
        通过 ``subprocess`` 运行 ``cmd`` 获取系统输出

    - ``cmd`` 为数组形式
    - 需要符合 ``subprocess`` 调用标准
    -  返回

       -  err信息,
       -  使用 ``换行符\\n`` 分隔的数组

    :param cmd:
    :type cmd: list, str
    :return:
    :rtype:
    """
    _e, op = None, ''
    if not isinstance(cmd, list):
        cmd = cmd.split(' ')

    try:
        op = subprocess.check_output(cmd)
        if sys.version_info[0] >= 3:
            op = to_str(op)
        op = op.split('\n')
    except Exception as err:
        _e = err

    return _e, op


def add_jpg(pathin):
    if not os.path.exists(pathin):
        log.debug('{} not exist'.format(pathin))
        return

    for root, dirs, files in os.walk(pathin):
        for f in files:
            ext = f.split('.')
            _fpth = os.path.join(root, f)
            if len(ext) != 1:
                if ext[-1] == 'jpg':
                    print('skip', _fpth)
                    continue

            os.rename(_fpth, '{}.jpg'.format(_fpth))


def num_choice(choices, depth=1):
    """
        传入数组, 返回正确的 index

    :param depth:
    :param choices:
    :type choices:
    :return:
    :rtype:
    """
    if not choices:
        return None

    with textui.indent(4, quote=' {}'.format(icons.icons[depth - 1])):
        # if len(choices) < 20:
        for i, choice in enumerate(choices, start=1):
            textui.puts(textui.colored.green('{}. {}'.format(i, choice)))
        # else:
        #     click.echo_via_pager('\n'.join('{}'.format(x) for x in choices))

    _valid = [str(x + 1) for x in range(0, len(choices))]
    c = click.prompt(click.style('[Depth: ({})]Your Choice(q-quit/b-back)?', fg='cyan').format(depth))

    if str(c) in 'qQ':
        os._exit(-1)
    elif str(c) in 'bB':
        return c
    elif c not in _valid:
        log.error('Invalid input :( [{}]'.format(c))
        return num_choice(choices)
    else:
        return int(c) - 1


def yn_choice(msg):
    """
    传入 msg , 返回 True/False
    :param msg:
    :type msg:
    :return:
    :rtype:
    """
    click.secho('{}? [yn]'.format(msg), nl=False, fg='green')
    c = click.getchar()
    click.echo()
    if c in 'yYnN':
        return 'yYnN'.index(c) < 2
    else:
        click.secho('only yYnN allowed :( [{}]'.format(c), fg='red')
        return yn_choice(msg)


if __name__ == '__main__':
    add_jpg('/Users/lihe/Documents/edisk/d4')
