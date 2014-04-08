#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 应用 / API v1 / 账户
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

from weiyu.shortcuts import http, jsonview
from weiyu.utils.decorators import only_methods

from ...utils.viewhelpers import jsonreply, parse_form

from ...auth import ident
from ...auth import user

IDENT_CHECK_RETCODE_MAP = {
        ident.IDENT_OK: (True, ident.IDENT_OK, ),
        ident.CHECK_IDENT_NOTFOUND: (False, 2, ),
        ident.CHECK_IDENT_INVALID_INPUT: (False, 257, ),
        ident.CHECK_IDENT_WRONG: (False, 13, ),
        }


@http
@jsonview
def account_stat_v1_view(request, userid):
    raise NotImplementedError


@http
@jsonview
def account_creat_v1_view(request):
    raise NotImplementedError


@http
@jsonview
def account_fcntl_v1_view(request, userid):
    raise NotImplementedError


@http
@jsonview
@only_methods(['POST', ])
def ident_query_v1_view(request):
    '''v1 实名信息查询接口.

    :Allow: POST
    :URL 格式: :wyurl:`api:ident-query-v1`
    :GET 参数: 无
    :POST 参数:
        ======== ========= ================================================
         字段     类型      说明
        ======== ========= ================================================
         number   unicode   **必须** 学号/工号
         idtype   int       **必须** 身份信息类型, 请参见实名信息模块文档
         idnum    unicode   **必须** 身份信息
        ======== ========= ================================================

    :返回:
        :r:
            ===== =========================================================
             0     验证通过
             2     给定的学号/工号不存在
             13    身份信息不匹配
             17    给定的学号/工号已有对应帐号
             22    传入参数格式不正确
             257   身份信息格式不正确
            ===== =========================================================

        若验证通过, 将返回所查询记录的基本信息:

            ==== ========= ================================================
            字段  类型      说明
            ==== ========= ================================================
             n    unicode   所查询个体的真实姓名.
             g    int       所查询个体的性别; 含义请参见实名信息模块文档.
             t    int       本条实名信息记录的类型.
            ==== ========= ================================================

        若所查询个体身份为学生, 返回还将包含一些学生特定的信息:

            ==== ========= ================================================
            字段  类型      说明
            ==== ========= ================================================
             ss   unicode   所属学院全称, 如 ``'数字媒体学院'``.
             sm   unicode   所属专业代码, 如 ``'0305'``.
             sc   int       所属班级序号, 从 1 开始.
             sy   int       入学年份.
            ==== ========= ================================================

    :副作用: 无

    '''

    try:
        number, idtype, idnum = parse_form(
                request,
                'number',
                'idtype',
                'idnum',
                )
    except KeyError:
        return jsonreply(r=22)

    try:
        idtype = int(idtype)
    except ValueError:
        return jsonreply(r=22)

    try:
        number = number.decode('utf-8')
        idnum = idnum.decode('utf-8')
    except ValueError:
        return jsonreply(r=22)

    # 检查是否已对应用户
    if user.User.find_by_ident(number) is not None:
        return jsonreply(r=17)

    # 核对身份信息
    chkresult = ident.FrozenIdent.check_ident(number, idtype, idnum)
    success, retcode = IDENT_CHECK_RETCODE_MAP[chkresult]
    if not success:
        return jsonreply(r=retcode)

    # 检查通过, 取记录, 返回信息
    fident = ident.FrozenIdent.fetch(number)
    typ = fident['type']
    result = {
            'r': 0,
            'n': fident['name'],
            'g': fident['gender'],
            't': typ,
            }

    if typ in ident.IDENT_TYPES_CURRENT_STUDENT:
        result.update({
                'ss': fident['student_school'],
                'sm': fident['student_major'],
                'sc': fident['student_class'],
                'sy': fident['student_year'],
                })

    return jsonreply(**result)


@http
@jsonview
@only_methods(['GET', ])
def ident_activate_v1_view(request, activation_key):
    '''v1 邮箱验证 (激活) 接口.

    因为本接口的用意是让用户从发送到注册邮箱的激活链接点击进入, 所以使用
    ``GET`` 方法而非 ``POST``.

    :Allow: GET
    :URL 格式: :wyurl:`api:ident-activate-v1`
    :GET 参数:
        ================ ========= ========================================
         字段             类型      说明
        ================ ========= ========================================
         activation_key   unicode   32 位激活 key
        ================ ========= ========================================

    :POST 参数: 无
    :返回:
        :r:
            ===== =========================================================
             0     邮箱验证 (激活) 成功
             2     给定的激活 key 不存在
             22    传入参数格式不正确
            ===== =========================================================

    :副作用:

        * 验证 (激活) 成功后:

            - 设置对应实名身份的激活 key 为已激活
            - 为对应的 User 对象添加 ``default`` 角色

    '''

    raise NotImplementedError


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
