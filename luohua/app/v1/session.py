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
from ...utils.viewhelpers import jsonreply, parse_form

from ..session import tokens


@http
@jsonview
@only_methods(['POST', ])
def session_auth_v1_view(request):
    '''v1 认证接口.

    :Allow: POST
    :URL 格式: :wyurl:`api:session-auth-v1`
    :GET 参数: 无
    :POST 参数:
        ======= ========= =================================================
         字段    类型      说明
        ======= ========= =================================================
         name    unicode   **必须** 登录名, 可取邮箱/学号
         pass    unicode   **必须** 密码的 SHA-512 hash 的十六进制表示
        ======= ========= =================================================

    :返回:
        :r:
            ==== ==========================================================
             0    认证成功
             5    认证失败, 用户名或密码错误
             17   认证失败, 无法唯一匹配用户 (正常情况不会出现; 详见代码)
             22   认证失败, 调用格式不正确
            ==== ==========================================================

        :t:
            如认证成功, 返回可以用来请求会话 cookie 的 token 字符串.
            认证不成功则该属性不存在.

    :副作用:
        * 认证成功时:

            - 为该请求 IP 及对应用户生成一个登陆 token

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
        return jsonreply(r=5)
    except ValueError:
        # 有多个匹配上的用户
        # 永远不应该出现; 注册部分的逻辑不会允许这种事情发生的.
        # 出现这种情况的话应该是手工编辑数据的原因了.
        return jsonreply(r=17)

    if not usr.chkpasswd(pass_):
        # 密码错误
        return jsonreply(r=5)

    # 签发 token
    token = tokens.request_token(request, 'login', usr['id'])
    return jsonreply(r=0, t=token)


@http
@jsonview
@only_methods(['POST', ])
def session_refresh_v1_view(request):
    '''v1 会话刷新接口.

    :Allow: POST
    :URL 格式: :wyurl:`api:session-refresh-v1`
    :GET 参数: 无
    :POST 参数:
        ======= ========= =================================================
         字段    类型      说明
        ======= ========= =================================================
         token   unicode   **必须** 由 ``session-auth-v1`` 接口派发的登陆
                           token
        ======= ========= =================================================

    :返回:
        :r:
            ===== =========================================================
             0     刷新会话成功
             5     给定的 token 不合法
             22    传入参数格式不正确
             257   当前会话已关联用户 (已登陆)
            ===== =========================================================

    :副作用:
        * 认证成功时:

            - 如请求未带 cookie 或 cookie 所示会话过期, 新建服务器端会话, 发送
              ``Set-Cookie`` HTTP 头
            - 在服务器会话中记录 UID
            - 刷新会话 ID

    '''

    if 'uid' in request.session:
        return jsonreply(r=257)

    try:
        token, = parse_form(request, 'token')
    except KeyError:
        return jsonreply(r=22)

    if not isinstance(token, six.text_type):
        return jsonreply(r=22)

    tok = tokens.query_token('login', token)
    if tok is None:
        # token 不存在
        return jsonreply(r=5)

    # 检查用户
    usr = user.User.fetch(tok['uid'])
    if usr is None:
        # token 指定的用户不存在... 销毁 token
        tokens.purge_token(token)
        return jsonreply(r=5)

    # 根据 token 设置会话
    request.session['uid'] = usr['id']
    request.session['login_token'] = usr['login_token']
    request.session['logged_in'] = True

    # 刷新会话 ID
    request.session.new_id()

    # TODO: 在全局用户状态里做相应设置

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
        :r: 常量 ``0``

    :副作用:
        * 注销成功时:
            - 从会话中删去 UID
            - 刷新会话 ID
            - 销毁本次使用的登陆 token

    '''

    # 微雨 Redis 后端的 __getitem__ 不会抛 KeyError 的
    uid, token = request.session['uid'], request.session['login_token']
    if uid is None or token is None:
        return jsonreply(r=0)

    del request.session['uid']
    del request.session['login_token']
    request.session['logged_in'] = False
    request.session.new_id()

    # 销毁 token
    tokens.revoke_token(request, 'login', uid, token)

    return jsonreply(r=0)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
