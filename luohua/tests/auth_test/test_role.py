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

from luohua.auth.role import Role, combine_caps


class TestRole(Case):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_fetch(self):
        assert Role.fetch('user')
        assert Role.fetch('nonexist') is None

    def test_caps(self):
        r = Role.fetch('user')

        caps = r['caps']
        assert isinstance(caps, set)
        assert caps == {'c1', 'c2', }

    def test_hascap(self):
        r = Role.fetch('user')

        assert r.hascap('c1')
        assert not r.hascap('c100')
        assert 'c2' in r
        assert 'c200' not in r

    def test_allcaps(self):
        caps = Role.allcaps('user', 'adm', )

        assert isinstance(caps, set)
        assert caps == {'c1', 'c2', 'c3', 'c5', }

    def test_grant_cap(self):
        r = Role()
        r['name'] = 'test'
        r['caps'] = {'1', }

        r.grant_cap('test')

        # 不能授予名字以减号开头的权限 (因为有歧义)
        assert_raises(ValueError, r.grant_cap, '-foo')
        assert r['caps'] == {'1', 'test', }

    def test_remove_cap(self):
        r = Role()
        r['name'] = 'test'
        r['caps'] = {'1', '2', }

        r.remove_cap('1')
        r.remove_cap('3')

        assert r['caps'] == {'2', }

    def test_ban_cap(self):
        r = Role()
        r['name'] = 'test'
        r['caps'] = {'1', }

        r.ban_cap('1')
        r.ban_cap('2')

        assert r['caps'] == {'-1', '-2', }

    def test_omni_cap(self):
        r = Role()
        r['name'] = 'root'
        r['caps'] = {'*', }
        assert r.hascap('random')
        assert r.hascap('things')

    def test_exclude_cap(self):
        r = Role()
        r['name'] = 'restricted-foo'
        r['caps'] = {'c1', '-c1', }

        # 拒绝权限优先授予权限
        assert not r.hascap('c1')

    def test_omni_cap_exclude(self):
        r = Role()
        r['name'] = 'restricted-root'
        r['caps'] = {'*', '-foo', }

        assert not r.hascap('foo')
        assert r.hascap('bar')

    def test_allcaps_exclude_cap(self):
        caps = Role.allcaps(['user', 'restricted-user', ])
        assert caps == {'c2', }

    def test_combine_caps(self):
        def combine_case(*args):
            return set(combine_caps(*args))

        case_0 = combine_case()
        case_1 = combine_case(['a', ], ['b', ], ['c', ], [], )
        case_2 = combine_case(['a', 'c', ], ['b', 'd', ], )
        case_3 = combine_case(['a', 'b', ], ['c', '-b', ], )
        case_4 = combine_case(['*', ], ['a', ], )
        case_5 = combine_case(['*', 'a', ], )
        case_6 = combine_case(['*', ], ['a', '-b', ], )

        assert case_0 == set([])
        assert case_1 == {'a', 'b', 'c', }
        assert case_2 == {'a', 'b', 'c', 'd', }
        assert case_3 == {'a', 'c', '-b', }
        assert case_4 == {'*', }
        assert case_5 == {'*', }
        assert case_6 == {'*', '-b', }


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
