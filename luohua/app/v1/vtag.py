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

from ...utils.viewhelpers import jsonreply, parse_form
from ...datastructures.vtag import VTag
from ...datastructures.vthread import VThread


@http
@jsonview
@only_methods(['POST', ])
def vtag_creat_v1_view(request, vtpid):
    '''v1 虚标签创建接口.

    :Allow: POST
    :URL 格式: ``vtp/<虚线索池 ID>/vtag/creat/``
    :POST 参数:
        ======== ======== =================================================
         字段     类型     说明
        ======== ======== =================================================
         vtagid   unicode  **可选** 希望拿到的虚标签 ID, 省略则自动生成
         name     unicode  **必须** 虚标签名称
         natural  int      **可选** 是否为自然虚标签, 为 ``1``
                           表示待创建的虚标签代表实际存在的一个版块,
                           为 ``0`` 表示此虚标签为程序生成. 默认为 ``1``
        ======== ======== =================================================

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
        vtagid, name, natural = parse_form(
                request,
                'vtagid',
                'name',
                'natural',
                vtagid=None,
                natural='1',
                )
    except KeyError:
        return jsonreply(r=22)

    if natural not in {'0', '1', }:
        return jsonreply(r=22)

    natural = natural == '1'

    # 判断是否重复
    if vtagid is not None and VTag.get(vtagid) is not None:
        return jsonreply(r=17)

    # 初始化虚标签对象并保存到数据库
    vtag = VTag()

    if vtagid is not None:
        vtag['id'] = vtagid

    vtag['name'] = smartstr(name)
    vtag['vtpid'] = vtpid
    vtag['natural'] = natural

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
    :URL 格式: ``vtp/<虚线索池 ID>/vtag/<虚标签 ID>/stat/``
    :POST 参数: 无
    :返回:
        :r:
            === ===========================================================
             0   查询成功
             2   所请求的虚标签不存在
            === ===========================================================

        :s:
            所请求虚标签的状态. 如果查询不成功, 此属性不存在.

            ======= ======== ==============================================
             字段    类型     说明
            ======= ======== ==============================================
             n       unicode  虚标签名称
             t       bool     是否为自然虚标签, ``false`` 表示程序自动生成
             x       dict     虚标签上附着的扩展属性
            ======= ======== ==============================================

    :副作用: 无

    '''

    vtag = VTag.get(vtagid)
    if vtag is None or vtag['vtpid'] != vtpid:
        return jsonreply(r=2)

    stat_obj = {
            'n': vtag['name'],
            't': vtag['natural'],
            'x': vtag['xattr'],
            }

    return jsonreply(r=0, s=stat_obj)


@http
@jsonview
@only_methods(['POST', ])
def vtag_getdents_v1_view(request, vtpid, vtagid):
    '''v1 虚线索列表接口.

    :Allow:  POST
    :URL 格式: ``vtp/<虚线索池 ID>/vtag/<虚标签 ID>/readdir/``
    :POST 参数:
            ======== ======== =============================================
             字段     类型     说明
            ======== ======== =============================================
             pagesz   int      **必须** 每页结果数, 最小 20, 最大 100
             cont     unicode  **可选** 上一页结果链接指针, 用它查询下一页.
                               如果省略则为查询第一页.
            ======== ======== =============================================

    :返回:
        :r:
            ==== ==========================================================
             0    查询成功
             2    所请求的虚标签不存在
             22   传入参数格式不正确
            ==== ==========================================================

        :l:
            一页虚线索的列表. 如果查询不成功, 此属性为空列表.

            列表中每个虚线索的形式如下.

            ======= ======== ==============================================
             字段    类型     说明
            ======= ======== ==============================================
             i       unicode  虚线索 ID
             t       unicode  虚线索标题
             o       unicode  虚线索所有者 ID
            ======= ======== ==============================================

        :c:
            下一页结果的链接指针, 将它再次传入此接口可以查询下一页的结果.
            如果当前页为最后一页, 此属性为空字符串.

            如果查询不成功, 此属性不存在.

    :副作用: 无

    '''

    try:
        pagesz, cont = parse_form(
                request,
                'pagesz',
                'cont',
                cont=None,
                )
    except KeyError:
        return jsonreply(r=22, l=[])

    if not pagesz.isdigit():
        return jsonreply(r=22, l=[])

    pagesz = int(pagesz)
    if not 20 <= pagesz <= 100:
        return jsonreply(r=22, l=[])

    vtag = VTag.get(vtagid)
    if vtag is None or vtag['vtpid'] != vtpid:
        return jsonreply(r=2, l=[])

    result, continuation_box = [], []
    cont_receiver = lambda x: continuation_box.append(x)
    for vth in VThread.from_vtag(vtag['id'], pagesz, cont, cont_receiver):
        result.append({
                'i': vth['id'],
                't': vth['title'],
                'o': vth['owner'],
                })

    return jsonreply(r=0, l=result, c=continuation_box[0])


@http
@jsonview
def vtag_fcntl_v1_view(request, vtpid, vtagid):
    raise NotImplementedError


@http
@jsonview
def vtag_unlink_v1_view(request, vtpid, vtagid):
    raise NotImplementedError


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
