#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 应用 / API v1 / 会话
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

from ...auth import user
from ...rt import pubsub
from ...utils.viewhelpers import jsonreply, parse_form


@http
@jsonview
@only_methods(['POST', ])
def session_login_v1_view(request):
    '''v1 登陆接口.

    :Allow: POST
    :URL 格式: :wyurl:`api:session-login-v1`
    :GET 参数: 无
    :POST 参数:
        ======= ========= =================================================
         字段    类型      说明
        ======= ========= =================================================
         name    unicode   **必须** 登录名, 可能是邮箱/ID/学号之类的信息
         pass    unicode   **必须** 密码的 SHA-512 hash 的十六进制表示
        ======= ========= =================================================

    :返回:
        :r:
            === ===========================================================
             0   登陆成功
             1   登陆失败, 用户名或密码错误
             2   登陆失败, 无法唯一匹配用户 (见代码实现)
             22   登陆失败, 调用格式不正确
            === ===========================================================

    :副作用:
        * 登陆成功时:

            - 如请求未带 cookie 或 cookie 所示会话过期, 新建服务器端会话, 发送
              ``Set-Cookie`` HTTP 头
            - 在服务器会话中记录 UID
            - 向该用户的实时消息频道发送 ``online`` 事件

    '''

    try:
        name, pass_ = parse_form(
                request,
                'name',
                'pass',
                )
    except KeyError:
        return jsonreply(r=22)

    try:
        assert isinstance(name, six.text_type)
        assert isinstance(pass_, six.text_type)
    except AssertionError:
        return jsonreply(r=22)

    if len(pass_) != 128:
        # 密码长度不符合 SHA-512 的十六进制 hash
        return jsonreply(r=22)

    try:
        usr = user.User.find_by_guess(name)
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
    request.session['uid'] = usr['id']
    request.session['logged_in'] = True
    # TODO: 在全局用户状态里做相应设置

    # 发送通知
    # TODO: 加上终端类型!
    pubsub.publish_user_event(usr['id'], 'online')

    return jsonreply(r=0)


@http
@jsonview
@only_methods(['POST', ])
def session_logout_v1_view(request):
    '''v1 注销接口.

    :Allow: POST
    :URL 格式: :wyurl:`api:session-logout-v1`
    :GET 参数: 无
    :POST 参数: 无
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
            - 向该用户的实时消息频道发送 ``offline`` 事件

    '''

    # 微雨 Redis 后端的 __getitem__ 不会抛 KeyError 的
    uid = request.session['uid']
    if uid is None:
        return jsonreply(r=1)

    del request.session['uid']
    request.session['logged_in'] = False
    request.session.new_id()

    # 发送通知
    # 之所以放在实际注销动作后边, 是为了万一通知发送过程出现异常不会影响
    # 注销的正常进行
    pubsub.publish_user_event(uid, 'offline')

    return jsonreply(r=0)


@http
@jsonview
@only_methods(['GET', ])
def session_ping_v1_view(request):
    '''v1 Ping 测试接口.

    :Allow: GET
    :URL 格式: :wyurl:`api:session-ping-v1`
    :GET 参数: 无
    :POST 参数: 无
    :返回:
        :r: 常数 0
        :m: 常量字符串 ``'pong'``
        :s: 会话 ID

    :副作用: 无

    '''

    return jsonreply(r=0, m='pong', s=request.session.id)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
