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

try:
    import ujson as json
except ImportError:
    import json

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
@only_methods(['POST', ])
def account_creat_v1_view(request):
    '''v1 帐号注册接口.

    :Allow: POST
    :URL 格式: :wyurl:`api:account-creat-v1`
    :GET 参数: 无
    :POST 参数:
        ========== ========= ===============================================
         字段       类型      说明
        ========== ========= ===============================================
         name       unicode   **必须** 显示名称 (昵称)
         pass       unicode   **必须** 密码
         email      unicode   **必须** 注册邮箱地址
         mobile     unicode   **必须** 手机号码
         itype      int       **必须** 实名记录类型;
                              目前仅支持 ``0`` (在读本科生)
         inum       unicode   **必须** 编号, 如学号/工号等
         idtype     int       **必须** 身份信息类型;
                              目前仅支持 ``0`` (身份证号后六位)
         idnum      unicode   **必须** 身份信息
         iinfo      dict      **必须** JSON 格式的实名记录详细信息 (见下)
         htmlmail   int       **必须** 如注册成功, 发送验证邮件的类型.
                              为 ``0`` 发送纯文本邮件,
                              为 ``1`` 发送 HTML 邮件
        ========== ========= ===============================================

        当 ``itype`` 为 ``0`` (在读本科生) 时, 要求 ``iinfo``
        字段内容具有以下形式:

        =========== ========= =============================================
         字段        类型      说明
        =========== ========= =============================================
         dorm_bldg   int       **必须** 寝室所在楼号
         dorm_room   unicode   **必须** 寝室房间号
        =========== ========= =============================================

        其他字段有效性要求:

        * ``name`` 不允许超过 16 个 Unicode 字符,
          且不允许与系统中已有显示名称重复.

    :返回:
        :r:
            ===== =========================================================
             0     注册成功
             22    传入参数格式不正确
             28    系统今日注册用户量已达最大值
             257   创建用户失败
            ===== =========================================================

        :e:
            如果创建用户失败, 这里返回对应阶段的错误码 (TODO: 整理错误码文档),
            否则该属性不存在.

    :副作用:

        * 注册成功时:

            - 新建一条用户记录 (:class:`luohua.auth.user.User`)
            - 新建一条可变实名身份记录 (:class:`luohua.auth.ident.Ident`)
            - 向给定的邮箱发送一封邮件, 提示验证注册邮箱
            - 记录审计事件

    '''

    try:
        (
                name, pass_, email, mobile,
                itype, inum, idtype, idnum, iinfo, htmlmail,
                ) = parse_form(
                        request,
                        'name', 'pass', 'email', 'mobile',
                        'itype', 'inum', 'idtype', 'idnum',
                        'iinfo', 'htmlmail',
                        )
    except KeyError:
        return jsonreply(r=22)

    try:
        name = name.decode('utf-8')
        pass_ = pass_.decode('utf-8')
        email = email.decode('utf-8')
        mobile = mobile.decode('utf-8')
        itype = int(itype)
        inum = inum.decode('utf-8')
        idtype = int(idtype)
        idnum = idnum.decode('utf-8')
        iinfo = json.loads(iinfo)
        htmlmail = int(htmlmail)
    except ValueError:
        return jsonreply(r=22)

    if htmlmail not in {0, 1}:
        return jsonreply(r=22)
    htmlmail = htmlmail != 0

    if itype in ident.IDENT_TYPES_CURRENT_STUDENT:
        # 在读学生
        # 检查宿舍信息
        if iinfo.viewkeys() != {'dorm_bldg', 'dorm_room', }:
            return jsonreply(r=22)

        dorm_bldg, dorm_room = iinfo['dorm_bldg'], iinfo['dorm_room']

        # 构造传入参数
        ident_info = {
                'email': email,
                'mobile': mobile,
                'student_dorm_building': dorm_bldg,
                'student_dorm_room': dorm_room,
                }

        result = user.User.new_user(
                pass_,
                itype,
                inum,
                idtype,
                idnum,
                ident_info,
                name,
                htmlmail,
                request,
                )
        retcode = result[0]
        if retcode != 0:
            # 创建失败
            return jsonreply(r=257, e=retcode)

        # 创建成功, 不过没什么有价值的信息返回
        # (用户需要去验证邮箱, 然后再登陆)
        return jsonreply(r=0)

    # 无法处理的实名记录类型
    # 因为这个函数的代码结构原因 (提前根据 itype 取值分叉), 错误码不会由 user
    # 模块返回. 因此我们需要装作自己是 user 模块, 返回正确的错误码
    return jsonreply(r=257, e=ident.NEW_IDENT_TYPE_NOT_IMPL)


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
         number   unicode   **必须** 学号/工号等
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
