#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 大学信息 / 专业信息
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
        'MajorsInfo',
        ]

import yaml

from . import base

MAJORS_DATA_FILENAME = 'majors.yml'


class MajorsInfo(base.BaseUnivInfo):
    '''专业信息对象.'''

    data_filename = MAJORS_DATA_FILENAME


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
