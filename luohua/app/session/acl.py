#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 应用 / 会话管理模块 / 访问控制
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

from __future__ import unicode_literals, division, print_function

__all__ = [
        'fetch_user_or_die',
        'sync_session_user',
        'EACCES_reply',
        ]

from ...utils.viewhelpers import jsonreply
from ...auth.user import User


class ACLError(Exception):
    def __init__(self, reason):
        super(ACLError, self).__init__()
        self.reason = reason


def fetch_user_or_die(request):
    # 微雨的 Redis 会话后端对不存在的会话 key 请求不会抛异常, 而是直接返回
    # Redis 驱动库返回的 None, 那我们就适应一下
    uid = request.session['uid']
    print(uid)
    if uid is None:
        raise ACLError(0)

    user = User.fetch(uid)
    if user is None:
        return ACLError(1)

    return user


def sync_session_user(request):
    try:
        user = fetch_user_or_die(request)
    except ACLError as exc:
        request.session['logged_in'] = False
        del request.session['uid']
        return None, exc.reason

    request.session['logged_in'] = True
    return user, 0


def EACCES_reply(reason):
    return jsonreply(r=13, e=reason)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
