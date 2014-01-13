#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 认证 / 角色
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
        'has_cap',
        'combine_caps',
        'canonicalize_caps',
        'Role',
        ]

import six
import itertools

from weiyu.db.mapper import mapper_hub

from ..utils.dblayer import RiakDocument
from ..utils.stringop import escape_lucene

ROLE_STRUCT_ID = 'luohua.role'

OMNI_CAP = '*'


def _check_valid_cap(cap, allow_omni):
    '''检查权限名合法性.

    其实就是看下是不是空字符串, 还有第一个字符不能是减号, 如果是就抛异常.
    有些地方会用到全能权限, 这里也有相应的判断.

    '''

    if not cap:
        raise ValueError('capability name cannot be empty')

    if not allow_omni and cap == OMNI_CAP:
        raise ValueError('omni-capability cannot be used here')

    if cap[0] == '-':
        raise ValueError('minus sign cannot precede capability name')


def has_cap(caps, requested_cap):
    '''检查给定的权限表是否具备指定的权限, 指定权限可以是全能权限 (``*``).

    :param caps: 权限表, 需要是可迭代对象.
    :type caps: :data:`types.GeneratorType`
    :param requested_cap: 所请求的权限.
    :type requested_cap: :data:`six.text_type`
    :return: 权限检查的结果, :const:`True` 为具备所指权限, 反之不具备.
    :rtype: bool

    '''

    _check_valid_cap(requested_cap, True)

    caps_set = set(caps) if not isinstance(caps, set) else caps
    negative_caps = set(cap[1:] for cap in caps_set if cap[0] == '-')

    # 拒绝压倒一切
    if requested_cap in negative_caps:
        return False

    # 全能权限
    # 已经处理过拒绝权限了所以直接返回就行了
    if OMNI_CAP in caps_set:
        return True

    return requested_cap in caps_set


def combine_caps(*caps_list):
    '''组合多个权限列表为一个.

    :param caps_list: 多个权限表, 每个参数应该可迭代.
    :type caps_list: list
    :return: 传入权限列表组合成的权限集合.
    :rtype: set

    '''

    return set(itertools.chain(*caps_list))


def canonicalize_caps(caps):
    '''最简化权限表, 去除被剥夺的普通权限, 如有全能权限则去除所有普通权限.

    :param caps_list: 输入权限表.
    :type caps_list: list
    :return: 最简化的权限集合.
    :rtype: set

    '''

    caps_set = set(caps) if not isinstance(caps, set) else caps
    negative_caps = set(cap[1:] for cap in caps_set if cap[0] == '-')

    # 组分中有全能权限则无视所有非拒绝权限
    if OMNI_CAP in caps_set:
        result = {OMNI_CAP, }
        result.update('-' + cap for cap in negative_caps)
        return result

    result = set(cap for cap in caps_set if cap not in negative_caps)
    return result


class Role(RiakDocument):
    '''认证系统角色.

    角色是权限的载体, 每个用户属于 0 个或多个角色, 同时具有这些角色所授予的\
    权限. 权限用于控制用户能调用哪些受保护的函数.

    权限名称是字符串, 为避免歧义, 权限名称不能以半角减号 (``-``) 打头.

    权限有三种, 授予权限, 剥夺权限 (形如 ``-foo`` 的权限) 和全能权限 (``*``).
    授予权限是普通的权限种类, 程序正常使用的就是这类权限. 剥夺权限用于使\
    某权限不能获得, 可以把剥夺权限放在某个角色里, 为某些用户添加这样的角色可以\
    起到封禁的作用. 全能权限是默认开放所有可能的权限, 但同时受到剥夺权限的限制,
    一般只授予系统管理员.

    '''

    struct_id = ROLE_STRUCT_ID

    def __contains__(self, key):
        return self.hascap(key)

    def hascap(self, cap):
        '''测试此角色是否具有指定的权限.

        :param cap: 要测试的权限, 可以是全能权限 (``*``).
        :type cap: :data:`six.text_type`
        :return: 测试结果, :const:`True` 为具备, 反之不具备.
        :rtype: bool

        '''

        return has_cap(self['caps'], cap)

    @classmethod
    def allcaps(cls, rids):
        '''返回所请求角色 ID 列表中角色拥有的所有权限.

        :param rids: 角色 ID 列表.
        :type rids: list
        :return: 所请求角色的权限总和的集合.
        :rtype: set

        '''

        return combine_caps(*(r['caps'] for r in cls.fetch_multiple(rids)))

    def grant_cap(self, cap):
        '''授予该角色一个权限.

        :param cap: 要授予的权限, 可以是全能权限 (``*``).
        :type cap: :data:`six.text_type`
        :return: :const:`None`

        '''

        _check_valid_cap(cap, True)

        self['caps'].add(cap)

    def ban_cap(self, cap):
        '''使该角色不能获取所指定的权限.

        :param cap: 要防止获取的权限, 不能是全能权限 (``*``).
        :type cap: :data:`six.text_type`
        :return: :const:`None`

        '''

        _check_valid_cap(cap, False)

        self['caps'].add('-' + cap)

    def remove_cap(self, cap):
        '''从该角色上移除一个权限.

        和 :meth:`ban_cap` 不同, 移除的权限仍有可能从其他角色获取到.

        :param cap: 要移除的权限, 可以是全能权限 (``*``).
        :type cap: :data:`six.text_type`
        :return: :const:`None`

        '''

        _check_valid_cap(cap, True)

        try:
            self['caps'].remove(cap)
        except KeyError:
            pass


# 数据库序列化/反序列化
@mapper_hub.decoder_for(ROLE_STRUCT_ID, 1)
def role_dec_v1(data):
    return {
            'name': data['n'],
            'caps': set(data['c']),
            }


@mapper_hub.encoder_for(ROLE_STRUCT_ID, 1)
def role_enc_v1(role):
    assert 'name' in role
    assert isinstance(role['name'], six.text_type)
    assert 'caps' in role
    assert isinstance(role['caps'], set)
    assert all(isinstance(cap, six.text_type) for cap in role['caps'])

    return {
            'n': role['name'],
            'c': list(role['caps']),
            }


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
