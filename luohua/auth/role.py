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

import six

from weiyu.db.mapper import mapper_hub

from ..utils.dblayer import RiakDocument
from ..utils.stringop import escape_lucene

ROLE_STRUCT_ID = 'luohua.role'


class Role(RiakDocument):
    struct_id = ROLE_STRUCT_ID

    def __contains__(self, key):
        return self.hascap(key)

    def hascap(self, cap):
        '''测试此角色是否具有能力 ``cap``.'''

        return cap in self['caps']

    @classmethod
    def allcaps(cls, *rids):
        '''返回 ``roles`` 列表所示角色拥有的所有能力.'''

        result = set()
        for role in cls.fetch_multiple(rids):
            result.update(role['caps'])

        return result


# 数据库序列化/反序列化
@mapper_hub.decoder_for(ROLE_STRUCT_ID, 1)
def role_dec_v1(data):
    return {
            'name': data['n'],
            'caps': data['c'],
            }


@mapper_hub.encoder_for(ROLE_STRUCT_ID, 1)
def role_enc_v1(role):
    assert 'name' in role
    assert isinstance(role['name'], six.text_type)
    assert 'caps' in role
    assert isinstance(role['caps'], (list, tuple,  ))
    assert all(isinstance(cap, six.text_type) for cap in role['caps'])

    return {
            'n': role['name'],
            'c': role['caps'],
            }


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
