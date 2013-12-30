#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 测试套件 / 认证 / 用户
#
# Copyright (C) 2013 JNRain
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
    def test_find_by_name(self):
        email1 = 'fsck+qq@youknow.com'
        email2 = 'nonexistent@in.testsuite.my'

        assert User.find_by_name('test0')['alias'] == 'test0'
        assert User.find_by_name(email1)['email'] == email1
        assert_raises(KeyError, User.find_by_name, email2, )

    # 密码验证测试
    def test_chkpasswd(self):
        # new hash
        test0 = User.find_by_name('test0')
        assert test0.chkpasswd('testtest')
        assert not test0.chkpasswd('deadf00d')

        # KBS hash
        test2 = User.find_by_name('test2')
        assert test2.chkpasswd('woshiruomima')
        assert not test2.chkpasswd('th1s-1z_mUCh>S7r0nG3r')


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
