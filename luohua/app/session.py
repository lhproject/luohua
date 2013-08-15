#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 应用 / 会话
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

from weiyu.shortcuts import *
from weiyu.utils.decorators import only_methods

from ..auth.user import User
from ..utils.viewhelpers import jsonreply, parse_form


@http
@jsonview
@only_methods(['POST', ])
def session_login_v1_view(request):
    '''v1 登陆接口.

    :Allow: POST
    :参数:
        ======= ======== ==================================================
         字段    类型     说明
        ======= ======== ==================================================
         name    unicode  **必须** 登录名, 可能是邮箱/ID/学号之类的信息
         pass    unicode  **必须** 密码
         lease   int      **可选** 登陆会话 cookie 保存时间

                          ================= ============
                           取值              保留时间
                          ================= ============
                           0 或省略          仅本次会话
                           1                 1 天
                           7                 1 周
                           14                2 周
                           30                1 月
                          ================= ============

        ======= ======== ==================================================

    :返回:
        :r:
            === ===========================================================
             0   登陆成功
             1   登陆失败, 用户名或密码错误
             2   登陆失败, 无法唯一匹配用户 (见代码实现)
             3   登陆失败, 调用格式不正确
            === ===========================================================

    :副作用:
        * 登陆成功时:
            - 如请求未带 cookie 或 cookie 所示会话过期, 新建服务器端会话, 发送
              ``Set-Cookie`` HTTP 头
            - 在服务器会话中记录 UID

    '''

    try:
        name, pass_, lease = parse_form(request, 'name', 'pass', 'lease', lease=0)
    except KeyError:
        return jsonreply(r=3)

    if not lease.isdigit():
        return jsonreply(r=3)

    lease = int(lease)
    if lease not in (0, 1, 7, 14, 30):
        return jsonreply(r=3)

    try:
        usr = User.find(name)
    except KeyError:
        # 没有拥有这个登陆身份的用户
        return jsonreply(r=2)
    except ValueError:
        # 有多个匹配上的用户
        # 永远不应该出现; 注册部分的逻辑不会允许这种事情发生的.
        # 出现这种情况的话应该是手工编辑数据的原因了.
        return jsonreply(r=2)

    if not usr.chkpasswd(pass_):
        # 密码错误
        return jsonreply(r=1)

    # 密码验证通过, 设置会话
    request.session['uid'] = usr['uid']
    if lease:
        request.session.set_cookie_prop(86400 * lease)
    # TODO: 在全局用户状态里做相应设置

    return jsonreply(r=0)


@http
@jsonview
@only_methods(['POST', ])
def session_logout_v1_view(request):
    '''v1 注销接口.

    :Allow: POST
    :参数: 无
    :返回:
        :r:
            === ===========================================================
             0   注销成功
             1   注销不成功, 很可能是因为当前并没有登陆
            === ===========================================================

    :副作用:
        * 注销成功时:
            - 从会话中删去 UID
            - 刷新会话 ID

    '''

    if 'uid' not in request.session:
        return jsonreply(r=1)

    del request.session['uid']
    request.session.new_id()

    return jsonreply(r=0)


@http
@jsonview
@only_methods(['GET', ])
def session_ping_v1_view(request):
    '''v1 Ping 测试接口.

    :Allow: GET
    :参数: 无
    :返回:
        :r: 常数 0
        :m: 常量字符串 ``'pong'``
        :s: 会话 ID

    :副作用: 无

    '''

    return jsonreply(r=0, m='pong', s=request.session.id)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
