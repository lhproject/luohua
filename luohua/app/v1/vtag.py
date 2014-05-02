#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 应用 / API v1 / 虚标签
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

from weiyu.helpers.misc import smartstr
from weiyu.shortcuts import http, jsonview
from weiyu.utils.decorators import only_methods

from ..session.decorators import require_cap
from ...utils.viewhelpers import jsonreply, parse_form
from ...datastructures.vtag import VTag
from ...datastructures.vthread import VThread
from ...utils.sequences import time_ascending_short_suffixed


@http
@jsonview
@only_methods(['POST', ])
@require_cap('vtag-creat')
def vtag_creat_v1_view(request, vtpid):
    '''v1 虚标签创建接口.

    :Allow: POST
    :URL 格式: :wyurl:`api:vtag-creat-v1`
    :GET 参数:
        ======= ========= =================================================
         字段    类型     说明
        ======= ========= =================================================
         vtpid   unicode   虚线索池 ID
        ======= ========= =================================================

    :POST 参数:
        ========= ========= ===============================================
         字段     类型      说明
        ========= ========= ===============================================
         vtagid    unicode   **可选** 希望拿到的虚标签 ID, 省略则自动生成
         name      unicode   **必须** 虚标签名称
         desc      unicode   **可选** 虚标签描述
        ========= ========= ===============================================

    :返回:
        :r:
            ==== ==========================================================
             0    创建成功
             17   希望拿到的虚标签 ID 已被占用
             22   传入参数格式不正确
            ==== ==========================================================

        :t: 新建虚标签的 ID. 如果创建不成功, 此属性不存在.

    :副作用:
        如果调用成功, 会在指定的虚线索池中创建一个虚标签.
        调用不成功则无副作用.

    '''

    try:
        vtagid, name, desc = parse_form(
                request,
                'vtagid',
                'name',
                'desc',
                vtagid=None,
                desc='',
                )
    except KeyError:
        return jsonreply(r=22)

    # 判断是否重复
    if vtagid is not None and VTag.fetch(vtagid) is not None:
        return jsonreply(r=17)

    # 初始化虚标签对象并保存到数据库
    vtag = VTag()

    if vtagid is not None:
        vtag['id'] = vtagid
    else:
        # 使用一个简短一点的 ID...
        vtag['id'] = time_ascending_short_suffixed()

    vtag['name'] = smartstr(name)
    vtag['desc'] = smartstr(desc)
    vtag['vtpid'] = vtpid
    vtag['natural'] = True

    # 不设置 xattr 的原因参见 vpool.py 相应注释
    vtag['xattr'] = {}

    vtag.save()

    return jsonreply(r=0, t=vtag['id'])


@http
@jsonview
@only_methods(['GET', ])
def vtag_stat_v1_view(request, vtpid, vtagid):
    '''v1 虚标签状态接口.

    :Allow:  GET
    :URL 格式: :wyurl:`api:vtag-stat-v1`
    :GET 参数:
        ======== ========= ================================================
         字段     类型     说明
        ======== ========= ================================================
         vtpid    unicode   虚线索池 ID
         vtagid   unicode   虚标签 ID
        ======== ========= ================================================

    :POST 参数: 无
    :返回:
        :r:
            === ===========================================================
             0   查询成功
             2   所请求的虚标签不存在
            === ===========================================================

        :s:
            所请求虚标签的状态. 如果查询不成功, 此属性不存在.

            ======= ========= =============================================
             字段    类型      说明
            ======= ========= =============================================
             n       unicode   虚标签名称
             d       unicode   虚标签描述
             t       bool      是否为自然虚标签,
                               ``false`` 表示程序自动生成
             x       dict      虚标签上附着的扩展属性
            ======= ========= =============================================

    :副作用: 无

    '''

    vtag = VTag.fetch(vtagid)
    if vtag is None or vtag['vtpid'] != vtpid:
        return jsonreply(r=2)

    stat_obj = {
            'n': vtag['name'],
            'd': vtag['desc'],
            't': vtag['natural'],
            'x': vtag['xattr'],
            }

    return jsonreply(r=0, s=stat_obj)


@http
@jsonview
@only_methods(['GET', ])
def vtag_getdents_v1_view(request, vtpid, vtagid, time_start, time_end):
    '''v1 虚线索列表接口.

    :Allow: GET
    :URL 格式: :wyurl:`api:vtag-getdents-v1`
    :GET 参数:
        ============ ========= ============================================
         字段         类型     说明
        ============ ========= ============================================
         vtpid        unicode   虚线索池 ID
         vtagid       unicode   虚标签 ID
         time_start   int       起始时间戳
         time_end     int       结束时间戳
        ============ ========= ============================================

    :POST 参数: 无
    :返回:
        :r:
            ==== ==========================================================
             0    查询成功
             2    所请求的虚标签不存在
             22   传入参数格式不正确
            ==== ==========================================================

        :l:
            最后变化时间在所查询时间段内虚线索的列表. 如果查询不成功,
            此属性为空列表.

            列表中每个虚线索的形式如下.

            ====== ========= ==============================================
             字段   类型      说明
            ====== ========= ==============================================
             i      unicode   虚线索 ID
             t      unicode   标题
             o      unicode   所有者 ID
             c      int       创建时间戳
             m      int       最后变化时间戳
            ====== ========= ==============================================

    :副作用: 无

    '''

    if not time_start.isdigit() or not time_end.isdigit():
        return jsonreply(r=22, l=[])

    time_start, time_end = int(time_start), int(time_end)

    vtag = VTag.fetch(vtagid)
    if vtag is None or vtag['vtpid'] != vtpid:
        return jsonreply(r=2, l=[])

    result = []
    for vth in VThread.from_vtag_mtime(vtag['id'], time_start, time_end):
        result.append({
                'i': vth['id'],
                't': vth['title'],
                'o': vth['owner'],
                'c': vth['ctime'],
                'm': vth['mtime'],
                })

    return jsonreply(r=0, l=result)


@http
@jsonview
def vtag_fcntl_v1_view(request, vtpid, vtagid):
    raise NotImplementedError


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
