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
from weiyu.db.mapper.base import Document

from ..utils.stringop import escape_lucene
from .passwd import Password

USER_STRUCT_ID = 'luohua.user'
mapper_hub.register_struct(USER_STRUCT_ID)


class User(Document):
    struct_id = USER_STRUCT_ID

    def __init__(self, data=None, uid=None, rawobj=None):
        super(User, self).__init__()

        if data is not None:
            # 使用解码后的形式作为数据
            # 这里调用 dict 的构造函数在 CPython 下有 overhead, 不过在 profile
            # 之前还是算了吧, 不太值得优化
            # 虽说留着没什么问题... 但看上去很不优雅. 那么换用更批量一点的形式
            # super(User, self).__init__(**self.decode(data))
            self.update(self.decode(data))

        if uid is not None:
            self['id'] = uid

        self._rawobj = rawobj

    def chkpasswd(self, psw):
        '''进行密码验证。'''

        psw_obj = self['password']
        return psw_obj.check(psw)

    @classmethod
    def _from_obj(cls, obj):
        return cls(obj.data, obj.key, obj) if obj.exists else None

    @classmethod
    def find(cls, uid):
        '''按文档 ID 获取一个用户.'''

        with cls.storage as conn:
            obj = conn.get(uid)
            return cls._from_obj(obj)

    @classmethod
    def find_by_name(cls, name):
        '''寻找登陆身份符合 name 的用户。'''

        name_escaped = escape_lucene(name)
        with cls.storage as conn:
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

            # protobuf 协议要求查询字串必须是字节流, 所以编个码
            # HTTP 协议无所谓, unicode 或者 bytes 都可以
            result = conn.search(query_expr.encode('utf-8'))

            # 检查下结果的数量, 应该只有一个. 如果不是一个就抛异常
            num, docs = result['num_found'], result['docs']
            if num == 0:
                raise KeyError(name_escaped)
            elif num > 1:
                raise ValueError(
                        'Found >1 user with login identity %s: %s' % (
                            repr(name_escaped),
                            repr(docs),
                            )
                        )

            # 拿出 ID, 生成对象返回
            uid = docs[0]['id']
            obj = conn.get(uid)
            return cls._from_obj(obj)

    def save(self):
        with self.storage as conn:
            obj = self._rawobj if self._rawobj is not None else conn.new()
            obj.key, obj.data = self.get('id'), self.encode()

            obj.store()

            # 刷新对象关联信息
            self['id'], self._rawobj = obj.key, obj


# 数据库序列化/反序列化
@mapper_hub.decoder_for(USER_STRUCT_ID, 1)
def user_dec_v1(data):
    # KBS 兼容性...
    alias = data.get('a', None)

    return {
            'password': Password(alias or uid, data['p']),
            'alias': alias,
            'email': data['e'],
            'roles': data['r'].split(' '),
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
    assert isinstance(user['roles'], list)
    assert 'xattr' in user
    assert isinstance(user['xattr'], dict)

    return {
            'p': user['password'].make_hash(),
            'a': user['alias'],
            'e': user['email'],
            'r': ' '.join(user['roles']),
            'x': user['xattr'],
            }


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
