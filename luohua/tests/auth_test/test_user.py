#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 测试套件 / 认证 / 用户
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

from luohua.auth.user import User

from ..fixtures import TEST_USERS


class TestUser(Case):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    # 匹配登陆身份测试
    def test_find_by_ident(self):
        number1, number2 = '1030512202', '0123456789'

        assert User.find_by_ident(number1)['alias'] == 'test2'
        assert User.find_by_ident(number2) is None

    def test_find_by_alias(self):
        alias1, alias2 = 'test0', 'nonexistent'

        assert User.find_by_alias(alias1)['ident'] == '1030513101'
        assert User.find_by_alias(alias2) is None

    def test_find_by_display_name(self):
        nd1, nd2 = '-灰 煮 牛-', 'test2'

        assert User.find_by_display_name(nd1)['ident'] == '1030513101'
        assert User.find_by_display_name(nd2) is None

    def test_find_by_guess(self):
        assert User.find_by_guess('1030512202')['alias'] == 'test2'
        assert User.find_by_guess('叫我曹尼玛')['alias'] == 'test2'
        assert User.find_by_guess('test0')['ident'] == '1030513101'

    # 密码验证测试
    def test_chkpasswd(self):
        # new hash
        test0 = User.find_by_alias('test0')
        assert test0.chkpasswd('testtest')
        assert not test0.chkpasswd('deadf00d')

        # KBS hash
        test2 = User.find_by_alias('test2')
        assert test2.chkpasswd('woshiruomima')
        assert not test2.chkpasswd('th1s-1z_mUCh>S7r0nG3r')


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
