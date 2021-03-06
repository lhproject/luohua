#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 数据结构 / 虚线索池
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

VTP_STRUCT_ID = 'luohua.vtp'


class VPool(RiakDocument):
    '''虚线索池.

    本结构的存储后端应为 Riak.

    .. note::
        ``VPool`` 的简称取成 ``vtp`` 而不是 ``vp`` 的原因是 ``vp``
        会和视频编码算法 VP 系列冲突.

    '''

    struct_id = VTP_STRUCT_ID

    def __init__(self, data=None, vtpid=None, rawobj=None):
        super(VPool, self).__init__(data, vtpid, rawobj)


@VPool.decoder(1)
def vtp_dec_v1(data):
    return {
            'name': data['n'],
            'natural': data['t'],
            'xattr': data['x'],
            }


@VPool.encoder(1)
def vtp_enc_v1(vtp):
    assert 'name' in vtp
    assert isinstance(vtp['name'], six.text_type)
    assert 'natural' in vtp
    assert isinstance(vtp['natural'], bool)
    assert 'xattr' in vtp
    assert isinstance(vtp['xattr'], dict)

    return {
            'n': vtp['name'],
            't': vtp['natural'],
            'x': vtp['xattr'],
            }


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
