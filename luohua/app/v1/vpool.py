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

from weiyu.helpers.misc import smartstr
from weiyu.shortcuts import http, jsonview
from weiyu.utils.decorators import only_methods

from ...utils.viewhelpers import jsonreply, parse_form
from ...datastructures.vpool import VPool
from ...datastructures.vtag import VTag


@http
@jsonview
@only_methods(['POST', ])
def vpool_creat_v1_view(request):
    '''v1 虚线索池创建接口.

    :Allow: POST
    :URL 格式: ``vtp/creat/``
    :POST 参数:
        ======== ======== =================================================
         字段     类型     说明
        ======== ======== =================================================
         vtpid    unicode  **可选** 希望拿到的虚线索池 ID, 省略则自动生成
         name     unicode  **必须** 虚线索池名称
         natural  int      **可选** 是否为自然虚线索池, 为 ``1``
                           表示待创建的虚线索池代表实际存在的一个内容集合,
                           为 ``0`` 表示此虚线索池为程序生成. 默认为 ``1``
        ======== ======== =================================================

    :返回:
        :r:
            ==== ==========================================================
             0    创建成功
             17   希望拿到的虚线索池 ID 已被占据
             22   传入参数格式不正确
            ==== ==========================================================

        :t: 新建虚线索池的 ID. 如果创建不成功, 此属性不存在.

    :副作用: 如果调用成功, 会创建一个虚线索池. 调用不成功则无副作用.

    '''

    try:
        vtpid, name, natural = parse_form(
                request,
                'vtpid',
                'name',
                'natural',
                vtpid=None,
                natural='1',
                )
    except KeyError:
        return jsonreply(r=22)

    if natural not in {'0', '1', }:
        return jsonreply(r=22)

    natural = natural == '1'

    # 如果有指定 ID 的话就先判断是否会重复
    if vtpid is not None and VPool.find(vtpid) is not None:
        # 所请求的 vtpid 已经被占据了
        return jsonreply(r=17)

    # 初始化虚线索池对象并保存到数据库
    vtp = VPool()

    if vtpid is not None:
        vtp['id'] = vtpid

    vtp['name'] = smartstr(name)
    vtp['natural'] = natural

    # 因为序列化不一定方便, 就不在这里一并初始化了, 反正是 API v1,
    # 留待 v2 再解决好了. 非得用的话就 vpool-fcntl 吧
    vtp['xattr'] = {}

    vtp.save()

    return jsonreply(r=0, t=vtp['id'])


@http
@jsonview
@only_methods(['GET', ])
def vpool_stat_v1_view(request, vtpid):
    '''v1 虚线索池状态接口.

    :Allow: GET
    :URL 格式: ``vtp/<虚线索池 ID>/stat/``
    :POST 参数: 无
    :返回:
        :r:
            === ===========================================================
             0   查询成功
             2   所请求的虚线索池不存在
            === ===========================================================

        :s:
            所请求虚线索池的状态. 如果查询不成功, 此属性不存在.

            ====== ======== ===============================================
             字段   类型     说明
            ====== ======== ===============================================
             n      unicode  虚线索池名称
             t      bool     是否为自然虚线索池, ``false`` 表示程序自动生成
             x      dict     虚线索池上附着的扩展属性
            ====== ======== ===============================================

    :副作用: 无

    '''

    vtp = VPool.find(vtpid)
    if vtp is None:
        return jsonreply(r=2)

    stat_obj = {
            'n': vtp['name'],
            't': vtp['natural'],
            'x': vtp['xattr'],
            }

    return jsonreply(r=0, s=stat_obj)


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
