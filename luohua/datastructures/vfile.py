#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 数据结构 / 虚文件
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

import functools

import six

from ..auth import user
from ..utils import dblayer

VF_STRUCT_ID = 'luohua.vf'

VF_FORMAT_PLAIN = 'txt'
VF_FORMAT_UBB = 'ubb'
VF_FORMAT_MARKDOWN = 'md'
VF_SUPPORTED_FORMATS = frozenset({
        VF_FORMAT_PLAIN,
        VF_FORMAT_UBB,
        VF_FORMAT_MARKDOWN,
        })


@functools.total_ordering
class VFile(dblayer.RiakDocument):
    '''虚文件.

    本结构的存储后端应为 Riak.

    '''

    struct_id = VF_STRUCT_ID

    def __init__(self, data=None, vfid=None, rawobj=None):
        super(VFile, self).__init__(data, vfid, rawobj)

    def __eq__(self, other):
        return (self['ctime'], self['id']) == (other['ctime'], other['id'])

    def __lt__(self, other):
        # 时间顺序排列, 其次是 ID
        return (self['ctime'], self['id']) < (other['ctime'], other['id'])


@VFile.decoder(1)
def vf_dec_v1(data):
    return {
            'owner': data['o'],
            'ctime': data['c'],
            'title': data['t'],
            'content': data['n'],
            'format': data['f'],
            'xattr': data['x'],
            }


@VFile.encoder(1)
def vf_enc_v1(vf):
    assert 'owner' in vf
    assert isinstance(vf['owner'], dict)
    assert 'ctime' in vf
    assert isinstance(vf['ctime'], six.integer_types)
    assert 'title' in vf
    assert isinstance(vf['title'], six.text_type)
    assert 'content' in vf
    assert isinstance(vf['content'], six.text_type)
    assert 'format' in vf
    assert isinstance(vf['format'], six.text_type)
    assert vf['format'] in VF_SUPPORTED_FORMATS
    assert 'xattr' in vf
    assert isinstance(vf['xattr'], dict)

    return {
            'o': vf['owner'],
            'c': vf['ctime'],
            't': vf['title'],
            'n': vf['content'],
            'f': vf['format'],
            'x': vf['xattr'],
            }


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
