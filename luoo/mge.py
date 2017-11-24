# -*- coding: utf-8 -*-
from __future__ import print_function

__author__ = 'lihe <imanux@sina.com>'
__date__ = '20/10/2017 11:44 AM'
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

from mongoengine import *

from base.abc import cfg

mg_cfg = {
    'host': cfg.get('mg.host', 'localhost'),
    'port': cfg.get('mg.port', 27027),
    'db': cfg.get('mg.db', 'luoo'),
    'alias': cfg.get('mg.alias', 'luoo_rw'),
    'username': cfg.get('mg.username', ''),
    'password': cfg.get('mg.password', ''),
}

connect(**mg_cfg)


class Volumes(Document):
    """期刊音乐详情

    """
    vol_index = IntField()
    vol_num = StringField()
    title = StringField()
    cover = StringField()

    tags = ListField()
    desc = StringField()
    pub_date = StringField()
    pub_author = DictField()
    track_count = IntField()
    tracks = ListField()

    meta = {
        'db_alias': mg_cfg.get('alias'),
        'collection': 'luoo.volumes',
        'ordering': [
            '-vol_index',
            '-vol_num',
            '-pub_date',
        ]
    }


class MusicVolumes(Document):
    """期刊音乐信息概要

    """
    vol_index = IntField()
    vol_num = StringField()
    favor = IntField()
    comments = IntField()
    title = StringField()
    cover = StringField()

    meta = {
        'db_alias': mg_cfg.get('alias'),
        'collection': 'luoo.music.volumes',
        'ordering': [
            '-vol_index',
            '-vol_num',
            '-comments',
            '-favor',
        ]
    }


class VolumeTracks(Document):
    """期刊音乐详细信息

    """
    vol_index = IntField()
    vol_num = StringField()
    stream_name = StringField()
    track_id = IntField()

    name = StringField()
    cover = StringField()

    artist = StringField()
    album = StringField()

    meta = {
        'db_alias': mg_cfg.get('alias'),
        'collection': 'luoo.volume.tracks',
        'ordering': [
            '-vol_index',
            '-vol_num',
            '-comments',
            '-favor',
        ]
    }


def save_music_volumes(dat):
    """存储概要信息

    :param dat:
    :type dat:
    :return:
    :rtype:
    """
    MusicVolumes.objects(
        vol_index=dat.get('vol_index'),
        vol_num=dat.get('vol_num'),
    ).update(
        upsert=True,
        vol_index=dat.get('vol_index'),
        vol_num=dat.get('vol_num'),
        title=dat.get('title'),
        cover=dat.get('cover'),
        favor=dat.get('favor', 0),
        comments=dat.get('comments', 0),
    )


def save_volumes(dat):
    """存储期刊详情, 及相应音乐信息

    :param dat:
    :type dat:
    :return:
    :rtype:
    """
    tracks = []
    if dat.get('tracks'):
        tracks = [t.get('track_id') for t in dat.get('tracks')]

    Volumes.objects(
        vol_index=dat.get('vol_index'),
        vol_num=dat.get('vol_num'),
    ).update(
        upsert=True,
        vol_index=dat.get('vol_index'),
        vol_num=dat.get('vol_num'),
        title=dat.get('title'),
        cover=dat.get('cover'),
        tags=dat.get('tags', []),
        desc=dat.get('desc'),
        pub_date=dat.get('pub_date'),
        pub_author=dat.get('pub_author'),
        track_count=len(tracks),
        tracks=tracks,
    )

    for track in dat.get('tracks'):
        VolumeTracks.objects(
            track_id=track.get('track_id'),
        ).update(
            upsert=True,
            vol_index=dat.get('vol_index'),
            vol_num=dat.get('vol_num'),
            stream_name=track.get('stream_name'),
            track_id=track.get('track_id'),
            name=track.get('name'),
            cover=track.get('cover'),
            artist=track.get('artist'),
            album=track.get('album'),
        )
