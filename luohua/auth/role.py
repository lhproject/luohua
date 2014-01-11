#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 认证 / 角色
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

from weiyu.db.mapper import mapper_hub
from weiyu.db.mapper.base import Document

from ..utils.stringop import escape_lucene

ROLE_STRUCT_ID = 'luohua.role'
mapper_hub.register_struct(ROLE_STRUCT_ID)


class Role(Document):
    struct_id = ROLE_STRUCT_ID

    def __init__(self, data):
        # 使用解码后的形式作为数据
        # 这里调用 dict 的构造函数在 CPython 下有 overhead, 不过在 profile
        # 之前还是算了吧, 不太值得优化
        # 虽说留着没什么问题... 但看上去很不优雅. 那么换用更批量一点的形式
        # super(User, self).__init__(**self.decode(data))
        self.update(self.decode(data))

    def __contains__(self, key):
        return self.hascap(key)

    def hascap(self, cap):
        '''测试此角色是否具有能力 ``cap``.'''

        return cap in self['caps']

    @classmethod
    def find(cls, name):
        '''寻找名为 name 的角色。'''

        name_escaped = escape_lucene(name)
        with cls.storage as conn:
            r = conn.search(('n:"%s"' % (name_escaped, )).encode('utf-8'))

            num, docs = r['num_found'], r['docs']
            if num == 0:
                raise KeyError(name_escaped)
            elif num > 1:
                raise ValueError(
                        'Found >1 role named %s: %s' % (
                            repr(name_escaped),
                            repr(docs),
                            )
                        )

            # 拿出 ID, 生成对象返回
            rid = docs[0]['id']
            data = conn.get(rid).data
            data['rid'] = rid
            return cls(data)

    @classmethod
    def allcaps(cls, *roles):
        '''返回 ``roles`` 列表所示角色拥有的所有能力.'''

        result = set()
        for role_name in roles:
            role = cls.find(role_name)
            result.update(role['caps'])

        return result


# 数据库序列化/反序列化
@mapper_hub.decoder_for(ROLE_STRUCT_ID, 1)
def role_dec_v1(data):
    rid = data.get('rid', None)

    return {
            'rid': rid,
            'name': data['n'],
            'caps': data['c'].split(' '),
            }


@mapper_hub.encoder_for(ROLE_STRUCT_ID, 1)
def role_enc_v1(role):
    return {
            'n': role['name'],
            'c': ' '.join(role['caps']),
            }


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
