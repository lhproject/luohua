#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 实时信道 / 会话状态
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
        'RTState',
        ]

from weiyu.db import db_hub

RT_STATE_STORAGE_ID = 'luohua.rt.state'


class RTState(object):
    def __init__(self, sid):
        self.sid = sid
        self.conn = db_hub.get_storage(RT_STATE_STORAGE_ID)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
