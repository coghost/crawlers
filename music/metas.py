# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '11/20 10:25'
__description__ = '''
mutagen
'''
import os
import sys
from pprint import pprint

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

from mutagen.id3 import ID3, TIT2, TALB, TPE1, APIC, PictureType, Encoding
from mutagen import mp3, id3
from izen import helper
from logzero import logger as zlog
from izen.helper import R, B, G


def get_file_info(name, prt=True):
    if prt:
        print(G.format('Found from local: ({})'.format(name)))
        print('-' * 32)

    has_pic = False
    m = mp3.MP3(name)
    song = ID3(name)

    # check if has picture
    for k, v in song.items():
        if "APIC" in k:
            has_pic = True
            break

    if prt:
        print('music info: {}'.format(B.format(m.info.pprint())))
        pprint(song.pprint())

    return has_pic, song


def update_file_info(name, dat=None):
    """ APIC:cover """
    dat = dat or {}
    song = ID3(name)
    before_update_size = helper.is_file_ok(name)
    tags = ['TIT2', 'TALB', 'TPE1']
    for tag in tags:
        if dat.get(tag) and dat.get(tag) != song.get(tag):
            song.add(getattr(id3, tag)(encoding=Encoding.UTF16, text=dat[tag]))

    if not song.get('APIC:cover') and dat.get('APIC'):
        print(G.format('update album picture'))
        with open(dat.get('APIC'), 'rb') as h:
            cover_raw = h.read()
        if cover_raw:
            frame = APIC(encoding=Encoding.UTF16, mime="image/jpeg",
                         desc="cover", type=PictureType.COVER_FRONT, data=cover_raw)
            song.add(frame)

    song.save()
    print('-' * 32)
    after_size = helper.is_file_ok(name)
    for k, v in song.items():
        if 'APIC' not in k:
            print(k, v)
    print('update done: size from {} to {}, pic took {}'.format(before_update_size, after_size, after_size - before_update_size))
    print(helper.C.format('-' * 32))
