#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 应用 / API v1 / 大学信息
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

from weiyu.shortcuts import http, jsonview
from weiyu.utils.decorators import only_methods

from ...utils.viewhelpers import jsonreply, parse_form

from ... import univ

@http
@jsonview
@only_methods(['GET', ])
def univ_basic_v1_view(request):
    '''v1 大学基本信息查询接口.

    :Allow: GET
    :URL 格式: ``univ/basic/``
    :参数: 无
    :返回:
        :r: 常量 0
        :n: 大学名称
        :a: 大学的别名列表
        :d: 地址
        :p: 邮编
        :h: 首页 URL

    :副作用: 无

    '''

    info = univ.basic_info
    return jsonreply(
            r=0,
            n=info.name,
            a=info.aliases,
            d=info.address,
            p=info.postal,
            h=info.homepage,
            )


@http
@jsonview
@only_methods(['GET', ])
def univ_dorms_list_v1_view(request):
    '''v1 大学宿舍信息查询接口.

    :Allow: GET
    :URL 格式: ``univ/dorms/``
    :参数: 无
    :返回:
        :r: 常量 0
        :d: 本大学所有宿舍楼的信息. key 为楼号, value 格式如下:

            ==== ======== =================================================
            属性  类型     说明
            ==== ======== =================================================
             c    unicode  本楼所在校区名
             p    unicode  本楼所在组团名
             g    int      本楼学生性别; 取值含义请参见实名信息组件文档
            ==== ======== =================================================

    :副作用: 无

    '''

    dorm_data = univ.dorm_info.data
    result = {
            k: {
                'c': v['campus'],
                'p': v['group'],
                'g': v['gender'],
                }
            for k, v in six.iteritems(dorm_data)
            }

    return jsonreply(r=0, d=result)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
