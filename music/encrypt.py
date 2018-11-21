# -*- coding: utf-8 -*-
__author__ = 'lihe <imanux@sina.com>'
__date__ = '11/04 16:18'
__description__ = '''
- link ref: https://github.com/darknessomi/musicbox
'''
import sys
import base64
import binascii
import hashlib
import json
import os

app_root = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(app_root)

from Crypto.Cipher import AES
from izen import chaos

MODULUS = ('00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7'
           'b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280'
           '104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932'
           '575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b'
           '3ece0462db0a22b8e7')
PUBKEY = '010001'
NONCE = b'0CoJUm6Qyw8W8jud'


def md5(plain):
    return chaos.Chaos().encrypt(plain)


def encrypted_song_id(song_id):
    magic = bytearray('3go8&$8*3*3h0k(2)2', 'u8')
    song_id = bytearray(song_id, 'u8')
    magic_len = len(magic)
    for i, sid in enumerate(song_id):
        song_id[i] = sid ^ magic[i % magic_len]
    m = hashlib.md5(song_id)
    result = m.digest()
    result = base64.b64encode(result).replace(b'/', b'_').replace(b'+', b'-')
    return result.decode('utf-8')


def encrypted_request(text):
    """
        # type: (str) -> dict
    :param text:
    :type text:
    :return:
    :rtype:
    """
    data = json.dumps(text).encode('utf-8')
    secret = create_key(16)
    params = aes(aes(data, NONCE), secret)
    encseckey = rsa(secret, PUBKEY, MODULUS)
    return {'params': params, 'encSecKey': encseckey}


def aes(text, key):
    pad = 16 - len(text) % 16
    text = text + bytearray([pad] * pad)
    encryptor = AES.new(key, AES.MODE_CBC, b'0102030405060708')
    ciphertext = encryptor.encrypt(text)
    return base64.b64encode(ciphertext)


def rsa(text, pubkey, modulus):
    text = text[::-1]
    rs = pow(int(binascii.hexlify(text), 16), int(pubkey, 16), int(modulus, 16))
    return format(rs, 'x').zfill(256)


def create_key(size):
    return binascii.hexlify(os.urandom(size))[:16]


if __name__ == '__main__':
    p = create_key(10)
    print(p)
