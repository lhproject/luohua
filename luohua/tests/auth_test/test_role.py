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

from luohua.auth.role import has_cap, combine_caps, canonicalize_caps, Role


class TestRole(Case):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_fetch(self):
        assert Role.fetch('testuser')
        assert Role.fetch('nonexist') is None

    def test_caps(self):
        r = Role.fetch('testuser')

        caps = r['caps']
        assert isinstance(caps, set)
        assert caps == {'c1', 'c2', }

    def test_simple_cap(self):
        assert_raises(ValueError, has_cap, [], '')
        assert_raises(ValueError, has_cap, [], '-a')
        assert has_cap({'a', 'b', }, 'b')
        assert not has_cap({'a', 'b', }, 'c')

    def test_role_hascap(self):
        r = Role.fetch('testuser')

        assert r.hascap('c1')
        assert not r.hascap('c100')
        assert 'c2' in r
        assert 'c200' not in r

    def test_allcaps(self):
        caps = Role.allcaps(['testuser', 'testadm', ])

        assert isinstance(caps, set)
        assert caps == {'c1', 'c2', 'c3', 'c5', }

    def test_grant_cap(self):
        r = Role()
        r['name'] = 'test'
        r['caps'] = {'1', }

        r.grant_cap('test')
        assert r['caps'] == {'1', 'test', }

        # 不能授予名字以减号开头的权限 (因为有歧义)
        assert_raises(ValueError, r.grant_cap, '-foo')

        # 可以授予全能权限
        r.grant_cap('*')
        assert r['caps'] == {'*', '1', 'test', }

    def test_remove_cap(self):
        r = Role()
        r['name'] = 'test'
        r['caps'] = {'*', '1', '2', }

        r.remove_cap('1')
        r.remove_cap('3')
        r.remove_cap('*')
        assert r['caps'] == {'2', }

        # 这是不能这么用的
        assert_raises(ValueError, r.remove_cap, '')
        assert_raises(ValueError, r.remove_cap, '-123')

    def test_ban_cap(self):
        r = Role()
        r['name'] = 'test'
        r['caps'] = {'1', }

        r.ban_cap('1')
        r.ban_cap('2')

        assert r['caps'] == {'1', '-1', '-2', }

        # 不能 ban 掉全能权限和非法的权限名
        assert_raises(ValueError, r.ban_cap, '')
        assert_raises(ValueError, r.ban_cap, '-hehe')
        assert_raises(ValueError, r.ban_cap, '*')

    def test_omni_cap(self):
        assert has_cap({'*', }, '*')
        assert has_cap({'*', }, 'random')
        assert has_cap({'*', }, 'things')

    def test_exclude_cap(self):
        assert not has_cap({'c1', '-c1', }, 'c1')

    def test_omni_cap_exclude(self):
        assert not has_cap({'*', '-foo', }, 'foo')
        assert has_cap({'*', '-foo', }, 'bar')

    def test_allcaps_exclude_cap(self):
        caps = Role.allcaps(['testuser', 'restricted-user', ])
        assert caps == {'c1', 'c2', '-c1', }

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
        assert case_3 == {'a', 'b', 'c', '-b', }
        assert case_4 == {'*', 'a', }
        assert case_5 == {'*', 'a', }
        assert case_6 == {'*', 'a', '-b', }

    def test_canonicalize_caps(self):
        case_0 = canonicalize_caps(set([]))
        case_1 = canonicalize_caps({'a', 'b', 'c', })
        case_2 = canonicalize_caps({'a', 'b', 'c', '-b', })
        case_3 = canonicalize_caps({'*', 'a', })
        case_4 = canonicalize_caps({'*', 'a', '-b', })

        assert case_0 == set([])
        assert case_1 == {'a', 'b', 'c', }
        assert case_2 == {'a', 'c', '-b', }
        assert case_3 == {'*', }
        assert case_4 == {'*', '-b', }


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
