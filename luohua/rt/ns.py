#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 实时信道 / Socket.IO 命名空间
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

from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin

from weiyu.async import async_hub

from weiyu import VERSION_STR as weiyu_version
from .. import __version__ as luohua_version

from . import state


@async_hub.register_ns('socketio', '/rt')
class RTNamespace(BaseNamespace, BroadcastMixin):
    def get_initial_acl(self):
        return ['on_hello', ]

    def recv_connect(self):
        pass

    def recv_disconnect(self):
        print self.session
        rt_sid = self.session.get('rt_sid', None)
        if rt_sid is not None:
            # 注销自己的实时会话
            state.state_mgr.do_rt_logout(rt_sid)

        self.disconnect()

    def on_ping(self):
        self.emit('pong')

    def on_hello(self, data):
        request = self.request
        wsgi_session = request.session

        login_token = data['loginToken']
        if not login_token:
            # 现在就算是未登陆用户的会话都有发行对应的 token...
            # 再不提供简直就是作死
            self.disconnect()

        # token 验证
        rt_sid = state.state_mgr.do_rt_login(
                wsgi_session.id,
                request.user,
                login_token,
                )
        if rt_sid is None:
            # 验证不通过, 不放行
            self.disconnect()

        # 记住自己的实时会话 ID, 连接断开的时候要用到
        self.session['rt_sid'] = rt_sid

        self.emit('helloAck', {
                'rt_sid': rt_sid,
                'versions': {
                    'weiyu': weiyu_version,
                    'luohua': luohua_version,
                    },
                })


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
