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


@async_hub.register_ns('socketio', '/rt')
class RTNamespace(BaseNamespace, BroadcastMixin):
    def recv_connect(self):
        pass

    def recv_disconnect(self):
        self.disconnect()

    def on_ping(self):
        self.emit('pong')


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
