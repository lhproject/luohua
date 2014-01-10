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

from ..utils.dblayer import RiakDocument

VTAG_STRUCT_ID = 'luohua.vtag'
mapper_hub.register_struct(VTAG_STRUCT_ID)

VTAG_VTP_INDEX = 'vtp_bin'


class VTag(RiakDocument):
    '''虚标签.

    这是组织虚线索的单位, 存在于虚线索池中.
    大概可以理解成 BBS 中 "版面" 的概念, 不过虚线索并不局限于一个虚标签内
    (所以叫标签...).

    本结构的存储后端应为 Riak.

    '''

    struct_id = VTAG_STRUCT_ID
    uses_2i = True

    def __init__(self, data=None, vtagid=None, rawobj=None):
        super(VTag, self).__init__(data, vtagid, rawobj)

    @classmethod
    def from_vpool(cls, vtpid):
        '''返回指定虚线索池中所有虚标签.'''

        return cls._do_fetch_by_index(VTAG_VTP_INDEX, vtpid, None, None)

    def _do_sync_2i(self, obj):
        obj.set_index(VTAG_VTP_INDEX, self['vtpid'])
        return obj


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
