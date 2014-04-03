#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 大学信息 / 包
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
        'SUPPORTED_UNIVERSITIES',
        'DEFAULT_UNIVERSITY',
        'is_supported',
        'request_univ_data',
        'dorm_info',
        ]

import pkg_resources

from weiyu import registry


def _discover_univs():
    maybe_univ_dirs = pkg_resources.resource_listdir(__name__, 'data')

    # 这里直接拼路径也许会有安全问题, 但是只有在 d 取到类似
    # '../../../../../etc' 的值的时候才会出现, 那么这种情况应该就不可能了
    univ_dirs = [
            d
            for d in maybe_univ_dirs
            if pkg_resources.resource_isdir(__name__, 'data/' + d)
            ]

    return frozenset(univ_dirs)


SUPPORTED_UNIVERSITIES = _discover_univs()


def is_supported(univ):
    '''返回给定的大学是否被支持.'''

    return univ in SUPPORTED_UNIVERSITIES


def _check_univ_support(univ):
    if not is_supported(univ):
        raise RuntimeError('university not supported: {0}'.format(univ))


def request_univ_data(univ, filename):
    '''请求给定大学数据目录中的文件内容.'''

    _check_univ_support(univ)

    # 安全检查
    if '/' in filename:
        raise ValueError('slash char in path: {0}'.format(filename))

    path = 'data/{0}/{1}'.format(univ, filename)
    return pkg_resources.resource_string(__name__, path)


def _get_default_univ():
    univ_config = registry.request('luohua.univ')

    univ = univ_config['university']
    _check_univ_support(univ)
    return univ


DEFAULT_UNIVERSITY = _get_default_univ()

# 用默认大学初始化各个组件
from . import basic
from . import dorms

basic_info = basic.BasicInfo(DEFAULT_UNIVERSITY)
dorm_info = dorms.DormInfo(DEFAULT_UNIVERSITY)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
