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

import time

from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin

from weiyu.async import async_hub

from weiyu import VERSION_STR as weiyu_version
from .. import __version__ as luohua_version

from . import state

# 连接建立到必须发送 hello 消息的最长时间间隔, 单位: 秒.
# 超过此值指定时间间隔仍未发送 hello 的客户端将被断开.
INITIAL_TIMEOUT_SECS = 30

# 周期性刷新 Redis 内实时会话记录的时间间隔, 单位: 秒.
# 这是为了防止实时服务器重启后, 遗留下前一个实例来不及销毁的会话记录而设计的.
# 此间隔必须比 state 组件中的会话记录 TTL 短, 原因显而易见.
RT_SESSION_TOUCH_INTERVAL_SECS = 45


@async_hub.register_ns('socketio', '/rt')
class RTNamespace(BaseNamespace, BroadcastMixin):
    def get_initial_acl(self):
        return ['on_hello', ]

    def _initial_timeout_thread(self, timeout):
        time.sleep(timeout)
        if not self.session['hello_done']:
            self.disconnect()

    def _rt_session_touch_thread(self, interval):
        while True:
            time.sleep(interval)

            # 虽说这个值应该不会被修改, 在登陆成功的实时会话里也不会为空...
            # 还是小心一点为好
            rt_sid = self.session.get('rt_sid', None)
            if not rt_sid:
                return

            state.state_mgr.touch_rt_session(rt_sid)

    def recv_connect(self):
        # 限制 hello 必须尽快发生
        self.session['hello_done'] = False
        self.spawn(self._initial_timeout_thread, INITIAL_TIMEOUT_SECS)

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
        login_token = data['loginToken']
        if not login_token:
            # TODO: 给未登陆用户发行实时会话 ID
            # 现在暂时不让他们连接...
            self.emit('helloAck', {
                    'result': 'failed',
                    'canReconnect': False,
                    })
            self.disconnect()
            return
        else:
            # token 验证
            # 直接用登陆 token 验证, 省得断开连接了还一次一次又一次地刷新会话
            # 当然这么做的前提是通信要加密...
            # 所以我们需要默认 SSL 为开启 (见配置)
            rt_sid = state.state_mgr.do_rt_login(login_token)
            if rt_sid is None:
                # 验证不通过, 不放行
                self.disconnect()

        # 记住自己的实时会话 ID, 连接断开的时候要用到
        self.session['rt_sid'] = rt_sid

        self.emit('helloAck', {
                'result': 'ok',
                'rt_sid': rt_sid,
                'versions': {
                    'weiyu': weiyu_version,
                    'luohua': luohua_version,
                    },
                })

        # 表示 hello 序列已经完成
        self.session['hello_done'] = True

        # 启动实时会话 touch 线程
        self.spawn(
                self._rt_session_touch_thread,
                RT_SESSION_TOUCH_INTERVAL_SECS,
                )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
