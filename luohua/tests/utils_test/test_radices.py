#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 测试套件 / 工具 / 数制转换
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

from nose.tools import assert_raises

from ..utils import Case

from luohua.utils import radices


class TestRadices(Case):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_base36(self):
        from36, to36 = radices.from36, radices.to36

        assert from36('0') == 0
        assert from36('  -  0  ') == 0
        assert from36('10') == 36
        assert from36('abc') == 13368
        assert from36('ABC') == 13368
        assert from36('-abc') == -13368
        assert from36('3W5E11264SGSG') == 18446744073709551616

        assert to36(0) == '0'
        assert to36(36) == '10'
        assert to36(13368) == 'abc'
        assert to36(18446744073709551616) == '3w5e11264sgsg'
        assert to36(-18446744073709551616) == '-3w5e11264sgsg'

    def test_base62(self):
        from62, to62 = radices.from62, radices.to62

        assert from62('0') == 0
        assert from62('  +  1  ') == 1
        assert from62('  -  1  ') == -1
        assert from62('A') == 10
        assert from62('Z') == 35
        assert from62('a') == 36
        assert from62('z') == 61
        assert from62('10') == 62
        assert from62('LygHa16AHYG') == 18446744073709551616

        assert to62(0) == '0'
        assert to62(10) == 'A'
        assert to62(35) == 'Z'
        assert to62(36) == 'a'
        assert to62(61) == 'z'
        assert to62(62) == '10'
        assert to62(18446744073709551616) == 'LygHa16AHYG'
        assert to62(-18446744073709551616) == '-LygHa16AHYG'

    def test_base62_from62_invalid_input(self):
        assert_raises(ValueError, radices.from62, '10.0')


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
