#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 应用 / API v1 / 虚文件
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

try:
    import ujson as json
except ImportError:
    import json

import six
import time

from weiyu.helpers.misc import smartstr
from weiyu.shortcuts import http, jsonview
from weiyu.utils.decorators import only_methods

from ...utils.viewhelpers import jsonreply, parse_form
from ...datastructures.vtag import VTag
from ...datastructures.vthread import VThread, VThreadTree
from ...datastructures.vfile import VFile


@http
@jsonview
def vfile_stat_v1_view(request, vfid):
    '''v1 虚文件状态接口.

    :Allow: GET
    :URL 格式: ``vf/<虚文件 ID>/stat/``
    :POST 参数: 无
    :返回:
        :r:
            === ===========================================================
             0   查询成功
             2   所请求的虚文件不存在
            === ===========================================================

        :s:
            所请求虚文件的状态. 如果查询不成功, 此属性不存在.

            ====== ======== ===============================================
             字段   类型     说明
            ====== ======== ===============================================
             t      unicode  虚文件标题
             o      unicode  所有者 ID
             c      int      创建时间 Unix 时间戳
             l      int      内容长度
             x      dict     虚文件上附着的扩展属性
            ====== ======== ===============================================

    :副作用: 无

    '''

    vf = VFile.find(vfid)
    if vf is None:
        return jsonreply(r=2)

    stat_obj = {
            't': vf['title'],
            'o': vf['owner'],
            'c': vf['ctime'],
            'l': len(vf['content']),
            'x': vf['xattr'],
            }

    return jsonreply(r=0, s=stat_obj)


@http
@jsonview
def vfile_read_v1_view(request, vfid):
    '''v1 虚文件读取接口.

    :Allow: GET
    :URL 格式: ``vf/<虚文件 ID>/read/``
    :POST 参数: 无
    :返回:
        :r:
            === ===========================================================
             0   查询成功
             2   所请求的虚文件不存在
            === ===========================================================

        :s:
            所请求虚文件的内容. 如果查询不成功, 此属性不存在.
            比起 stat 接口唯一的差别是内容长度字段变成了实际的内容.

            ====== ======== ===============================================
             字段   类型     说明
            ====== ======== ===============================================
             t      unicode  虚文件标题
             o      unicode  所有者 ID
             c      int      创建时间 Unix 时间戳
             n      int      虚文件内容
             x      dict     虚文件上附着的扩展属性
            ====== ======== ===============================================

    :副作用: 无

    '''

    vf = VFile.find(vfid)
    if vf is None:
        return jsonreply(r=2)

    stat_obj = {
            't': vf['title'],
            'o': vf['owner'],
            'c': vf['ctime'],
            'n': vf['content'],
            'x': vf['xattr'],
            }

    return jsonreply(r=0, s=stat_obj)


@http
@jsonview
def vfile_creat_v1_view(request, vfid):
    raise NotImplementedError


@http
@jsonview
def vfile_fcntl_v1_view(request, vfid):
    raise NotImplementedError


@http
@jsonview
def vfile_unlink_v1_view(request, vfid):
    raise NotImplementedError


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
