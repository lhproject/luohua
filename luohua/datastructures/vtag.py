#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 数据结构 / 虚标签
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

VTAG_STRUCT_ID = 'luohua.vtag'
mapper_hub.register_struct(VTAG_STRUCT_ID)

VTAG_VTP_INDEX = 'vtp_bin'


class VTag(Document):
    '''虚标签.

    这是组织虚线索的单位, 存在于虚线索池中.
    大概可以理解成 BBS 中 "版面" 的概念, 不过虚线索并不局限于一个虚标签内
    (所以叫标签...).

    本结构的存储后端应为 Riak.

    '''

    struct_id = VTAG_STRUCT_ID

    def __init__(self, data=None, vtagid=None, rawobj=None):
        super(VTag, self).__init__()

        if data is not None:
            self.update(self.decode(data))

        if vtagid is not None:
            self['id'] = vtagid

        self._rawobj = rawobj

    @classmethod
    def _from_obj(cls, obj):
        return cls(obj.data, obj.key, obj) if obj.exists else None

    @classmethod
    def _do_fetch_by_index(cls, idx, key, max_results, continuation):
        with cls.storage as conn:
            page = conn.get_index(
                    idx,
                    key,
                    max_results=max_results,
                    continuation=continuation,
                    )
            for vthid in page.results:
                obj = conn.get(vthid)
                yield cls._from_obj(obj)

    @classmethod
    def from_vpool(cls, vtpid):
        '''返回指定虚线索池中所有虚标签.'''

        return cls._do_fetch_by_index(VTAG_VTP_INDEX, vtpid, None, None)

    @classmethod
    def find(cls, vtagid):
        '''按文档 ID 获取一个虚标签.'''

        with cls.storage as conn:
            obj = conn.get(vtagid)
            return cls._from_obj(obj)

    def save(self):
        '''保存虚标签到数据库.'''

        with self.storage as conn:
            obj = self._rawobj if self._rawobj is not None else conn.new()
            obj.key, obj.data = self.get('id'), self.encode()

            # 同步 2i 索引
            obj.set_index(VTAG_VTP_INDEX, self['vtpid'])

            obj.store()

            # 刷新对象关联信息
            self['id'], self._rawobj = obj.key, obj


@mapper_hub.decoder_for(VTAG_STRUCT_ID, 1)
def vtag_dec_v1(data):
    return {
            'name': data['n'],
            'vtpid': data['p'],
            'natural': data['t'],
            'xattr': data['x'],
            }


@mapper_hub.encoder_for(VTAG_STRUCT_ID, 1)
def vtag_enc_v1(vtag):
    assert 'name' in vtag
    assert isinstance(vtag['name'], six.text_type)
    assert 'vtpid' in vtag
    assert 'natural' in vtag
    assert isinstance(vtag['natural'], bool)
    assert 'xattr' in vtag
    assert isinstance(vtag['xattr'], dict)

    return {
            'n': vtag['name'],
            'p': vtag['vtpid'],
            't': vtag['natural'],
            'x': vtag['xattr'],
            }


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
