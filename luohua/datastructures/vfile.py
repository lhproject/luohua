#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 数据结构 / 虚文件
#
# Copyright (C) 2013 JNRain
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

VF_STRUCT_ID = 'luohua.vf'
mapper_hub.register_struct(VF_STRUCT_ID)


class VFile(Document):
    '''虚文件.

    本结构的存储后端应为 Riak.

    '''

    struct_id = VF_STRUCT_ID

    def __init__(self, data=None, vfid=None, rawobj=None):
        super(VFile, self).__init__()

        if data is not None:
            self.update(self.decode(data))

        if vfid is not None:
            self['id'] = vfid

        self._rawobj = rawobj

    @classmethod
    def find(cls, vfid):
        '''按文档 ID 获取一个虚文件.'''

        with cls.storage as conn:
            obj = conn.get(vfid)
            return cls(obj.data, obj.key, obj) if obj.exists else None

    @classmethod
    def find_multiple(cls, ids):
        '''按文档 ID 列表一次性获取多个虚文件.'''

        with cls.storage as conn:
            for vfid in ids:
                obj = conn.get(vfid)
                yield cls(obj.data, obj.key, obj) if obj.exists else None

    def save(self):
        '''保存虚文件到数据库.'''

        with self.storage as conn:
            # 文档 ID 未指定则自动生成
            obj = self._rawobj if self._rawobj is not None else conn.new()
            obj.key, obj.data = self.get('id'), self.encode()
            obj.store()
            self['id'] = obj.key


@mapper_hub.decoder_for(VF_STRUCT_ID, 1)
def vf_dec_v1(data):
    return {
            'owner': data['o'],
            'ctime': data['c'],
            'title': data['t'],
            'content': data['n'],
            'xattr': data['x'],
            }


@mapper_hub.encoder_for(VF_STRUCT_ID, 1)
def vf_enc_v1(vf):
    assert 'owner' in vf
    assert 'ctime' in vf
    assert 'title' in vf
    assert isinstance(vf['title'], six.text_type)
    assert 'content' in vf
    assert isinstance(vf['content'], six.text_type)
    assert 'xattr' in vf
    assert isinstance(vf['xattr'], dict)

    return {
            'o': vf['owner'],
            'c': vf['ctime'],
            't': vf['title'],
            'n': vf['content'],
            'x': vf['xattr'],
            }


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
