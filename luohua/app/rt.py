#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 应用 / 实时信道
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

from socketio import socketio_manage

from weiyu.async import async_hub
from weiyu.shortcuts import http, jsonview
from weiyu.utils.decorators import only_methods

from .session.decorators import require_cap

@http
@jsonview
# @require_cap('rt-open')
def rt_gateway_view(request):
    '''实时信道.

    :参数: 无
    :返回:
        如请求用户具备 ``rt-open`` 能力, 则不适用; 否则返回错误代码.

    :副作用:

        请求成功则会打开一条 Socket.IO 信道, 否则无副作用.

    '''

    socketio_manage(
            request.env,
            async_hub.get_namespaces('socketio'),
            request,
            None,  # error_handler
            json.loads,
            json.dumps,
            )

    return (
            204,
            {},
            {'request_vanished': True, },
            )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
