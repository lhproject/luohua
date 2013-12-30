#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 应用 / API v1 / 虚线索池
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

from weiyu.shortcuts import http, jsonview
from weiyu.utils.decorators import only_methods

from ...utils.viewhelpers import jsonreply, parse_form
from ...datastructures.vpool import VPool
from ...datastructures.vtag import VTag


@http
@jsonview
@only_methods(['GET', ])
def vpool_getdents_v1_view(request, vtpid):
    '''v1 虚标签列表接口.

    :Allow: GET
    :URL 格式: ``vtp/<虚线索池 ID>/readdir/``
    :POST 参数: 无
    :返回:
        :r:
            === ===========================================================
             0   查询成功
             2   所请求的虚线索池不存在
            === ===========================================================

        :t:
            所请求虚线索池中虚标签的列表. 不分页, 一次返回全部虚标签.

            如果查询不成功, 此列表为空.

            列表中每个元素的形式如下.

            ====== ======== ===============================================
             字段   类型     说明
            ====== ======== ===============================================
             i      unicode  虚标签 ID
             n      unicode  虚标签名称
            ====== ======== ===============================================

    :副作用: 无

    '''

    vtp = VPool.find(vtpid)
    if vtp is None:
        return jsonreply(r=2, t=[])

    result = []
    for vtag in VTag.from_vpool(vtp['id']):
        result.append({
                'i': vtag['id'],
                'n': vtag['name'],
                })

    return jsonreply(r=0, t=result)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
