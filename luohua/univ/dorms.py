#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 大学信息 / 宿舍信息
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
        'DormInfo',
        ]

import yaml

from . import request_univ_data

DORMS_DATA_FILENAME = 'dorms.yml'


class DormInfo(object):
    '''宿舍信息对象.'''

    def __init__(self, univ):
        # NOTE: 与 PyYAML 默认行为不同, 所有字符串都会被加载为 Unicode 类型.
        # 这是因为微雨框架加载配置文件时, 由 YAMLConfig 修改了 yaml 的 loader
        # 配置.
        self.data = yaml.load(request_univ_data(univ, DORMS_DATA_FILENAME))

    def query_building(self, bldg):
        '''查询某一号楼的信息.'''

        return self.data[bldg]

    def ip_to_building(self, address):
        '''根据 IP 查询对应宿舍楼信息.'''

        raise NotImplementedError


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
