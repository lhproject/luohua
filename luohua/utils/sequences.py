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
        'time_ascending_suffixed',
        'time_descending_suffixed',
        'ascending_ts',
        'descending_ts',
        ]

import time
import random

from .radices import to36

# 这是 UTC 时间 3058/10/26 03:46:08, 一千多年之后还会有人在用这个软件么...
# 抛开感伤, 这只是实现递减时间戳必须给定的一个 "时间尽头" 而已, 给到这个程度
# 既不会在可预见的未来撞上, 又不会让当下的递减时间戳数值太大, 那么差不多了
#
# 其实这里直接用 0x7fffffff 这个 Y2038 时间点貌似都可以= =! (前提是我们这软件
# 在 Y2038 之前就会废弃, oh no...)
TIMESTAMP_LIMIT = 1 << 35

PRNG = random.SystemRandom()


def _get_suffix():
    '''生成一个随机后缀字符串.'''

    return '%04x' % PRNG.randint(0, 0xffff)


def time_ascending(timestamp=None):
    '''生成一个随时间推移而比较顺序递增的字符串.'''

    ts_actual = timestamp if timestamp is not None else int(time.time())
    return to36(ts_actual)


def time_descending(timestamp=None):
    '''生成一个随时间推移而比较顺序递减的字符串.'''

    ts_actual = timestamp if timestamp is not None else int(time.time())
    return to36(TIMESTAMP_LIMIT - ts_actual)


def time_ascending_suffixed(timestamp=None):
    '''生成一个随时间推移而比较顺序递增的字符串, 带上一个随机后缀.'''

    return time_ascending(timestamp) + _get_suffix()


def time_descending_suffixed(timestamp=None):
    '''生成一个随时间推移而比较顺序递减的字符串, 带上一个随机后缀.'''

    return time_descending(timestamp) + _get_suffix()


def ascending_ts(timestamp=None):
    '''生成一个随时间推移递增的时间戳整数.'''

    return timestamp if timestamp is not None else int(time.time())


def descending_ts(timestamp=None):
    '''生成一个随时间推移递减的时间戳整数.'''

    return TIMESTAMP_LIMIT - (
            timestamp if timestamp is not None else int(time.time())
            )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
