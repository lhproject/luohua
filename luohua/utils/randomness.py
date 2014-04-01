#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 工具 / 随机性
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

import os
import base64


def b64(entropy_bytes):
    '''从操作系统请求随机字节, 并用 URL-safe Base64 编码.

    返回前, 还会截去末尾可能出现的 ``=`` 号.

    '''

    result = base64.urlsafe_b64encode(os.urandom(entropy_bytes))
    return result.strip('=')


def fixed_length_b64(length):
    '''返回一定长度的随机 Base64 字节.

    为使实现简单, 并考虑到实际需求, 本函数只能生成长度为 4 的倍数的随机 Base64
    串.

    '''

    # 为了简单, 这里人为限制 length 必须为 4 的倍数
    groups, rem = divmod(length, 4)
    if rem != 0:
        raise ValueError('only multiples of 4 are supported for now')

    return b64(groups * 3)


def salt(length):
    '''返回一定长度的适合作为 salt 使用的随机字符串.

    目前此函数是直接调用的 :func:`fixed_length_b64` 实现.

    '''

    # 现在这个实现其实就和随机 Base64 串一样一样的, 不过还是分开, 哪天换掉了
    # 也方便区分
    return fixed_length_b64(length)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
