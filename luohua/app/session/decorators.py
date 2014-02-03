#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 应用 / 会话管理模块 / 修饰符
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

__all__ = [
        'require_login',
        'require_cap',
        ]

import decorator

from .acl import EACCES_reply, sync_session_user
from ...auth.role import has_cap


def _require_login_fn_(fn, request, *args, **kwargs):
    user, exc_reason = sync_session_user(request)
    if user is None:
        return EACCES_reply(exc_reason)

    return fn(request, *args, **kwargs)


def require_login(fn):
    return decorator.decorator(_require_login_fn_, fn)


def require_cap(cap):
    def _decorator_(fn):
        def _wrapped_(fn, request, *args, **kwargs):
            user, exc_reason = sync_session_user(request)
            if user is None:
                return EACCES_reply(exc_reason)

            if not has_cap(user.caps, cap):
                return EACCES_reply(2)

            return fn(request, *args, **kwargs)

        return decorator.decorator(_wrapped_, fn)
    return _decorator_


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
