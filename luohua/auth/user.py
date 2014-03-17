#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 认证 / 用户
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

from __future__ import unicode_literals, division

import six

from ..utils.dblayer import RiakDocument
from ..utils.stringop import escape_lucene
from .passwd import Password
from .role import Role

USER_STRUCT_ID = 'luohua.user'

USER_ALIAS_IDX = 'user_alias_bin'
USER_IDENT_IDX = 'user_ident_bin'


class User(RiakDocument):
    struct_id = USER_STRUCT_ID
    uses_2i = True

    def __init__(self, data=None, uid=None, rawobj=None):
        super(User, self).__init__(data, uid, rawobj)

    def chkpasswd(self, psw):
        '''进行密码验证。'''

        psw_obj = self['password']
        return psw_obj.check(psw)

    @classmethod
    def find_by_ident(cls, ident):
        '''寻找实名身份符合 ident 的用户.'''

        # 按实名身份索引检索
        by_ident = list(cls._do_fetch_by_index(USER_IDENT_IDX, ident))
        if by_ident:
            # 当前情况下, 多于一个就报错
            if len(by_ident) > 1:
                raise ValueError('>1 user with the same ident: %s' % (ident, ))

            return by_ident[0]

        return None

    @classmethod
    def find_by_alias(cls, alias):
        '''寻找 KBS 帐户名符合 alias 的用户.'''

        # 按 KBS 帐户名索引检索
        by_alias = list(cls._do_fetch_by_index(USER_ALIAS_IDX, alias))
        if by_alias:
            # 同上
            if len(by_alias) > 1:
                raise ValueError('>1 user with the same alias: %s' % (alias, ))

            return by_alias[0]

        return None

    @classmethod
    def find_by_name(cls, name):
        '''寻找登陆身份符合 name 的用户.

        将按照以下顺序检测 ``name``:

        1. 学号/工号
        2. KBS 帐户名

        '''

        result_by_ident = cls.find_by_ident(name)
        if result_by_ident is not None:
            return result_by_ident

        result_by_alias = cls.find_by_alias(name)
        if result_by_alias is not None:
            return result_by_alias

        return None

    @property
    def caps(self):
        return Role.allcaps(self['roles'])

    def _do_sync_2i(self, obj):
        obj.set_index(USER_IDENT_IDX, self['ident'])

        if 'alias' in self:
            obj.set_index(USER_ALIAS_IDX, self['alias'])

        return obj


# 数据库序列化/反序列化
@User.decoder(1)
def user_dec_v1(data):
    # KBS 兼容性...
    alias = data.get('a', None)

    # NOTE: 密码的 uid 字段只有 KBS 的 hash 算法用到, 而只有 KBS 导入的用户
    # 才有 KBS 格式的 hash, 所以这里对没有设置别名的用户传入空字符串是完全
    # 没有问题的
    return {
            'password': Password(alias or '', data['p']),
            'alias': alias,
            'ident': data['i'],
            'roles': set(data['r']),
            'xattr': data['x'],
            }


@User.encoder(1)
def user_enc_v1(user):
    assert 'password' in user
    assert isinstance(user['password'], Password)
    assert 'alias' in user
    if user['alias'] is not None:
        assert isinstance(user['alias'], six.text_type)
    assert 'ident' in user
    assert isinstance(user['ident'], six.text_type)
    assert 'roles' in user
    assert isinstance(user['roles'], set)
    assert 'xattr' in user
    assert isinstance(user['xattr'], dict)

    return {
            'p': user['password'].psw_hash,
            'a': user['alias'],
            'i': user['ident'],
            'r': list(user['roles']),
            'x': user['xattr'],
            }


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
