#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 应用 / API v1 / 虚线索
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
from ...datastructures.vthread import VThread


@http
@jsonview
@only_methods(['GET', ])
def vthread_stat_v1_view(request, vthid):
    '''v1 虚线索状态接口.

    :Allow: GET
    :URL 格式: ``vth/<虚线索 ID>/stat/``
    :POST 参数: 无
    :返回:
        :r:
            ==== ==========================================================
             0    查询成功
             2    所请求的虚线索不存在
            ==== ==========================================================

        :s:
            所请求虚线索的状态. 如果查询不成功, 此属性不存在.

            ====== ======== ===============================================
             字段   类型     说明
            ====== ======== ===============================================
             t      unicode  虚线索标题
             o      unicode  虚线索所有者 ID
             g      list     所属虚标签 ID 的列表
             p      unicode  所属虚线索池 ID
             x      dict     虚线索上附着的扩展属性
            ====== ======== ===============================================

    :副作用: 无

    '''

    vth = VThread.find(vthid)
    if vth is None:
        return jsonreply(r=2)

    stat_obj = {
            't': vth['title'],
            'o': vth['owner'],
            'g': vth['vtags'],
            'p': vth['vtpid'],
            'x': vth['xattr'],
            }
    return jsonreply(r=0, s=stat_obj)


@http
@jsonview
@only_methods(['GET', ])
def vthread_getdents_v1_view(request, vthid):
    '''v1 虚文件列表接口.

    :Allow: GET
    :URL 格式: ``vth/<虚线索 ID>/readdir/``
    :POST 参数: 无
    :返回:
        :r:
            ==== ==========================================================
             0    查询成功
             2    所请求的虚线索不存在
            ==== ==========================================================

        :l:
            所请求虚线索中所有虚文件的层次结构列表, 形式如下::

                [
                  楼主虚文件,
                  [直接回复 1, 楼中楼回复 1, 楼中楼回复 2, ..., ],
                  [直接回复 2, ],
                  ...,
                ]

            如果查询不成功, 该属性不存在.

            .. note::

                **此 API 不分页**, 这是考虑到大多数线索不会很长而做出的设计.
                如有分页需求请在前端自行实现.

    :副作用: 无

    '''

    vth = VThread.find(vthid)
    if vth is None:
        return jsonreply(r=2)

    return jsonreply(r=0, l=vth['tree'].tree)


@http
@jsonview
def vthread_fcntl_v1_view(request, vthid):
    raise NotImplementedError


@http
@jsonview
def vthread_unlink_v1_view(request, vthid):
    raise NotImplementedError


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
