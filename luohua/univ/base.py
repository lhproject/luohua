#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 大学信息 / 基类
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
        'BaseUnivInfo',
        ]

import yaml

from . import request_univ_data, get_default_univ


class BaseUnivInfo(object):
    '''大学信息对象基类.'''

    data_filename = None

    def __init__(self, univ=None):
        assert self.data_filename is not None

        self.univ = univ
        self._data = None

    def _ensure_data(self):
        if self._data is not None:
            return

        # 默认大学存放在配置里, 所以不能在 import 阶段访问, 只能按需加载
        univ = self.univ or get_default_univ()

        # NOTE: 与 PyYAML 默认行为不同, 所有字符串都会被加载为 Unicode 类型.
        # 这是因为微雨框架加载配置文件时, 由 YAMLConfig 修改了 yaml 的 loader
        # 配置.
        self._data = yaml.load(request_univ_data(univ, self.data_filename))

    @property
    def data(self):
        self._ensure_data()
        return self._data


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
