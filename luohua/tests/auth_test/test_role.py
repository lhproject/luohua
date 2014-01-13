#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 测试套件 / 认证 / 角色
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
from ..shortcuts import *

from luohua.auth.role import Role


class TestRole(Case):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_find(self):
        assert Role.fetch('user')
        assert Role.fetch('nonexist') is None

    def test_caps(self):
        r = Role.fetch('user')

        caps = r['caps']
        caps.sort()

        assert tuple(caps) == ('c1', 'c2', )

    def test_hascap(self):
        r = Role.fetch('user')

        assert r.hascap('c1')
        assert not r.hascap('c100')
        assert 'c2' in r
        assert 'c200' not in r

    def test_allcaps(self):
        caps = list(Role.allcaps('user', 'adm', ))
        caps.sort()

        assert tuple(caps) == ('c1', 'c2', 'c3', 'c5', )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
