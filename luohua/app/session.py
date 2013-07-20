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
from ..utils.viewhelpers import jsonreply


@http('session-login-v1')
@jsonview
@only_methods(['POST', ])
def session_login_v1_view(request):
    '''v1 登陆接口.

    :方法: POST
    :参数:
        * ``name`` 登录名, 可能是邮箱/ID/学号之类的信息
        * ``pass`` 密码

    :返回:
        * ``{ "r": 0 }`` 登陆成功
        * ``{ "r": 1 }`` 登陆失败, 用户名或密码错误
        * ``{ "r": 2 }`` 登陆失败, 无法唯一匹配用户 (见代码实现)
        * ``{ "r": 3 }`` 登陆失败, 调用格式不正确

    '''

    try:
        name, pass_ = request.form['name'], request.form['pass']
    except KeyError:
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
    # TODO: 在全局用户状态里做相应设置

    return jsonreply(r=0)


@http('session-logout-v1')
@jsonview
@only_methods(['POST', ])
def session_logout_v1_view(request):
    '''v1 注销接口.

    :方法: POST
    :参数: 无
    :返回:
        * ``{ "r": 0 }`` 注销成功
        * ``{ "r": 1 }`` 注销不成功, 很可能是因为当前并没有登陆

    '''

    if 'uid' not in request.session:
        return jsonreply(r=1)

    del request.session['uid']
    return jsonreply(r=0)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
