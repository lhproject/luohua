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

from weiyu.db.mapper import mapper_hub

from ..utils.dblayer import RiakDocument
from ..utils.stringop import escape_lucene
from .passwd import Password

USER_STRUCT_ID = 'luohua.user'


class User(RiakDocument):
    struct_id = USER_STRUCT_ID

    def __init__(self, data=None, uid=None, rawobj=None):
        super(User, self).__init__(data, uid, rawobj)

    def chkpasswd(self, psw):
        '''进行密码验证。'''

        psw_obj = self['password']
        return psw_obj.check(psw)

    @classmethod
    def find_by_name(cls, name):
        '''寻找登陆身份符合 name 的用户。'''

        name_escaped = escape_lucene(name)
        # 这里假设存放用户数据的 bucket 上已经启用了 Riak Search
        # 并且定义了项目自带的 schema. 不启用 schema 在这里虽说没什么问题
        # 但也许会导致返回结果多出几个用不着的字段 (我没试),
        # 所以最好还是加上.
        #
        # Riak Search 的相关页面
        # http://docs.basho.com/riak/latest/dev/advanced/search/
        # 和 Search Schema 的内容
        # TODO: 根据 name 的形式 (含 '@', 全数字等) 在这里就定下查询字段
        query_expr = 'a:"%s" e:"%s"' % (name_escaped, name_escaped, )
        return cls.fetch_fts(query_expr)


# 数据库序列化/反序列化
@mapper_hub.decoder_for(USER_STRUCT_ID, 1)
def user_dec_v1(data):
    # KBS 兼容性...
    alias = data.get('a', None)

    # NOTE: 密码的 uid 字段只有 KBS 的 hash 算法用到, 而只有 KBS 导入的用户
    # 才有 KBS 格式的 hash, 所以这里对没有设置别名的用户传入空字符串是完全
    # 没有问题的
    return {
            'password': Password(alias or '', data['p']),
            'alias': alias,
            'email': data['e'],
            'roles': set(data['r']),
            'xattr': data['x'],
            }


@mapper_hub.encoder_for(USER_STRUCT_ID, 1)
def user_enc_v1(user):
    assert 'password' in user
    assert isinstance(user['password'], Password)
    assert 'alias' in user
    assert 'email' in user
    assert isinstance(user['email'], six.text_type)
    assert 'roles' in user
    assert isinstance(user['roles'], set)
    assert 'xattr' in user
    assert isinstance(user['xattr'], dict)

    return {
            'p': user['password'].make_hash(),
            'a': user['alias'],
            'e': user['email'],
            'r': list(user['roles']),
            'x': user['xattr'],
            }


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
