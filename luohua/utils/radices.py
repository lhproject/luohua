#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 工具 / 数制转换
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
        'from36',
        'to36',
        'from62',
        'to62',
        ]

# NOTE: 为什么不像注释掉的代码那样采用类似 C 的思路直接处理字符编码呢?
# 因为我想减少处理器执行代码时的 branching, 这几个数据结构 fit 进 L1 缓存
# 应该是问题不大的, 整体看来不会太影响性能. 而且更重要的是代码变得十分简单了
BASE36_MAP = '0123456789abcdefghijklmnopqrstuvwxyz'
BASE62_MAP = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
BASE62_INVERSE_MAP = {ord(ch): i for i, ch in enumerate(BASE62_MAP)}


def from36(s):
    '''把一个代表 36 进制数字的字符串转换为数字.

    36 进制中, 字母的大小写会被忽略.

    '''

    return int(s, 36)


def to36(x):
    '''把一个数字转换为对应的 36 进制字符串.

    转换成的字符串中字母全部为小写.

    '''

    # 防止返回空字符串
    if x == 0:
        return '0'

    sign = x >= 0
    temp, result = (x if sign else -x), []
    while temp > 0:
        temp, digit = divmod(temp, 36)

        # # 0x30 + d if d < 10 else 0x61 + d - 10
        # result.append(digit + (0x30 if digit < 10 else 0x57))
        result.append(BASE36_MAP[digit])

    # return ('' if sign else '-') + ''.join(chr(i) for i in result[::-1])
    return ('' if sign else '-') + ''.join(result[::-1])


def from62(s):
    '''把一个代表 62 进制数字的字符串转换为数字.

    数码的顺序是 0-9, A-Z, a-z (很显然区分大小写).

    '''

    # 预处理
    temp1 = s.strip()

    # 符号, 如有符号则判断是否为正号, 默认为正
    has_sign = temp1[0] in '+-'
    sign = temp1[0] == '+' if has_sign else True

    # 格式检查
    temp2 = temp1[1:].strip() if has_sign else temp1
    if not temp2.isalnum():
        # 故意模仿 Python int() 的错误信息
        raise ValueError('invalid literal for int() with base 62: ' + repr(s))

    result, exponent = 0, 1 if sign else -1
    for digit_chr in (ord(ch) for ch in temp2[::-1]):
        # if digit_chr < 0x40:
        #     # number
        #     digit = digit_chr - 0x30
        # elif digit_chr < 0x60:
        #     # uppercase letter
        #     # 0x41 ('A') - 10 = 0x37
        #     digit = digit_chr - 0x37
        # else:
        #     # lowercase letter
        #     # 0x61 ('a') - 36 = 0x3d
        #     digit = digit_chr - 0x3d

        # result += exponent * digit
        result += exponent * BASE62_INVERSE_MAP[digit_chr]
        exponent *= 62

    return result


def to62(x):
    '''把一个数字转换为对应的 62 进制字符串.'''

    # 防止返回空字符串
    if x == 0:
        return '0'

    sign = x >= 0
    temp, result = (x if sign else -x), []
    while temp > 0:
        temp, digit = divmod(temp, 62)

        # if digit < 10:
        #     # 0-9
        #     digit_chr = 0x30 + digit
        # elif digit < 36:
        #     # A-Z
        #     digit_chr = 0x37 + digit
        # else:
        #     # a-z
        #     digit_chr = 0x3d + digit

        # result.append(digit_chr)
        result.append(BASE62_MAP[digit])

    # return ('' if sign else '-') + ''.join(chr(i) for i in result[::-1])
    return ('' if sign else '-') + ''.join(result[::-1])


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
