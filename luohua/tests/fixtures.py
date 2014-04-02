#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 测试套件 / 预置数据
#
# Copyright (C) 2013-2014 JNRain
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals, division, print_function

import time
import six

from weiyu.helpers.misc import smartbytes
from luohua.auth.ident import FrozenIdent, Ident
from luohua.auth.user import User
from luohua.auth.role import Role

TEST_USERS = {
        '9fabe73980ff48aba62303812aa93765': {
            '_V': 1,
            'a': 'test0',
            'i': '1030513101',
            'nd': '-灰 煮 牛-',
            'ndm': int(time.time()),
            'p': (
                'lh1$ZcMloWnpTCDoCwXI|f9b2fcb14e85afd8333cc969275f27ab1343e7'
                '8a414c9c7f52507d5e53436df62f8f16f55fb383a1a9a88971b3f152566'
                '0e6ff6b6f49c2a9f1c7b9f58adce29c'
                ),
            'r': 'user',
            'x': {},
            },
        '0012cdf931a64c01ab97cb26f5f84bf0': {
            '_V': 1,
            'a': 'test2',
            'i': '1030512202',
            'nd': '叫我曹尼玛',
            'ndm': int(time.time() - 86400 * 32),  # 32 天前注册/改名的情况
            'p': 'kbs$0b84f4bb2b3c572572015dd1050b3232',
            'r': 'user adm',
            'x': {},
            },
        }

TEST_USERS_2I = {
        '9fabe73980ff48aba62303812aa93765': {
            'user_alias_bin': 'test0',
            'user_ident_bin': '1030513101',
            'user_nd_bin': '-灰 煮 牛-',
            },
        '0012cdf931a64c01ab97cb26f5f84bf0': {
            'user_alias_bin': 'test2',
            'user_ident_bin': '1030512202',
            'user_nd_bin': '叫我曹尼玛',
            },
        }

TEST_PASSWORDS = {
        '9fabe73980ff48aba62303812aa93765': 'testtest',
        '0012cdf931a64c01ab97cb26f5f84bf0': 'woshiruomima',
        }

TEST_ROLES = {
        'user': {
            '_V': 1,
            'n': '用户',
            'c': ['c1', 'c2', ],
            },
        'adm': {
            '_V': 1,
            'n': '鹳狸猿',
            'c': ['c2', 'c3', 'c5', ],
            },
        'restricted-user': {
            '_V': 1,
            'n': '受限用户',
            'c': ['-c1', ],
            },
        }

TEST_FROZEN_IDENTS = {
        '1030513101': {
            '_V': 1,
            't': 0,
            'n': '王尼玛',
            'g': 0,
            'it': 0,
            'in': '12345X',
            'ss': '数字媒体学院',
            'sm': '0305',
            'sc': 1,
            'sy': 2013,
            },
        '1030512202': {
            '_V': 1,
            't': 0,
            'n': '曹尼玛',
            'g': 0,
            'it': 0,
            'in': '543210',
            'ss': '数字媒体学院',
            'sm': '0305',
            'sc': 2,
            'sy': 2012,
            },
        }

TEST_IDENTS = {
        '1030513101': {
            '_V': 1,
            't': 0,
            'e': 'test0@example.com',
            'm': '12345671234',
            'ak': '~',
            'sdb': '清苑',
            'sdr': '123',
            },
        '1030512202': {
            '_V': 1,
            't': 0,
            'e': 'fsck+qq@youknow.com',
            'm': '98765434321',
            'ak': '~',
            'sdb': '清苑',
            'sdr': '321',
            },
        }


def users_setup():
    # 设置几个测试用户, 权限之类的数据
    with User.storage as conn:
        for uid, data in six.iteritems(TEST_USERS):
            obj = conn.new(uid, data)

            # 2i
            for idx_k, idx_v in six.iteritems(TEST_USERS_2I[uid]):
                # 采用 protobuf 协议连接 Riak 的话这里必须是 bytes 类型
                obj.set_index(smartbytes(idx_k), smartbytes(idx_v))

            obj.store()

            print('[+User] %s' % uid)


def users_teardown():
    # 把测试数据扔掉
    with User.storage as conn:
        for uid in TEST_USERS:
            conn.get(uid).delete()
            print('[-User] %s' % uid)


def roles_setup():
    with Role.storage as conn:
        for rid, data in six.iteritems(TEST_ROLES):
            conn.new(rid, data).store()
            print('[+Role] %s' % rid)


def roles_teardown():
    with Role.storage as conn:
        for rid in TEST_ROLES:
            conn.get(rid).delete()
            print('[-Role] %s' % rid)


def frozen_ident_setup():
    with FrozenIdent.storage as conn:
        for number, data in six.iteritems(TEST_FROZEN_IDENTS):
            conn.new(number, data).store()
            print('[+FIdent] %s' % number)


def frozen_ident_teardown():
    with FrozenIdent.storage as conn:
        for number in TEST_FROZEN_IDENTS:
            conn.get(number).delete()
            print('[-FIdent] %s' % number)


def ident_setup():
    with Ident.storage as conn:
        for number, data in six.iteritems(TEST_IDENTS):
            conn.new(number, data).store()
            print('[+Ident] %s' % number)


def ident_teardown():
    with Ident.storage as conn:
        for number in TEST_IDENTS:
            conn.get(number).delete()
            print('[-Ident] %s' % number)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
