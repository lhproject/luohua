#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 工具 / 序列生成
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
        'time_ascending',
        'time_descending',
        'descending_ts',
        ]

import time
import random

from .radices import to36

TIMESTAMP_LIMIT = 0x7fffffffffffffff

PRNG = random.SystemRandom()


def time_ascending(timestamp=None):
    '''生成一个随时间推移而比较顺序递增的字符串.'''

    ts = timestamp if timestamp is not None else int(time.time())
    return to36(ts) + ('%04d' % PRNG.randint(0, 9999))


def time_descending(timestamp=None):
    '''生成一个随时间推移而比较顺序递减的字符串.'''

    ts = timestamp if timestamp is not None else int(time.time())
    return to36(TIMESTAMP_LIMIT - ts) + ('%04d' % PRNG.randint(0, 9999))


def descending_ts(timestamp=None):
    '''生成一个随时间推移递减的时间戳整数.'''

    ts = timestamp if timestamp is not None else int(time.time())
    return TIMESTAMP_LIMIT - ts


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
