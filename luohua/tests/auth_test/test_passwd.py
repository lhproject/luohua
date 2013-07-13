#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 测试套件 / 认证 / 密码
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

from ..utils import Case
from ..shortcuts import *

from luohua.auth import passwd


class TestPassword(Case):
    @classmethod
    def setup_class(cls):
        # 这个其实是从已经消失的 weiyu.auth 包的测试套件里继承的测试数据
        # hash 部分简单修改了下
        uid = cls.uid = 'testuser123'
        psw1 = cls.psw1 = '*JE&%5e^&YU4w%ftWRtfSEfAEt%$&Ww47%6w56T#Wtq345q2'
        psw2 = cls.psw2 = r"-+|0\\!n.eOO!>UFg lO`J3_/1p)kLB'"
        hash1_kbs = cls.hash1_kbs = 'kbs$db36e2d26576ccc8e36239e8b767a0de'
        hash2_kbs = 'kbs$56a52bf0a79a247139fba25f8751a15e'
        hash1_lh1 = (
                'lh1$pwCyJLoiMcsGZaPn|7a6e6337bea5e6b15c8ac602ef279d516c210'
                'a63e4432d71f9fedd04fce65d062823d312337186212b13c36e588d0ec'
                '0038d54a3678b563c55c68000b1b523a9'
                )

        passwds = cls.passwds = []
        passwds.append(passwd.Password(uid, hash1_kbs))
        passwds.append(passwd.Password(uid, hash2_kbs))
        passwds.append(passwd.Password(uid, hash1_lh1))

        cases = cls.cases = []
        cases.append((psw1, True, ))
        cases.append((psw1, False, ))
        cases.append((psw1, True, ))

    @classmethod
    def teardown_class(cls):
        pass

    # 密码验证测试
    def test_chkpasswd(self):
        for psw, (input_pw, should_pass, ) in zip(self.passwds, self.cases):
            assert psw.check(input_pw) == should_pass

    # 密码创建测试
    # 先创建, 再确认用原始密码可以通过验证
    def test_create_kbs(self):
        psw_obj = passwd.KBSHashAlgorithm.create(self.uid, self.psw1)

        # 对 KBS 这种不随机加盐的 hash 而言可以多一层 sanity 防护
        assert str(psw_obj.alg) == self.hash1_kbs
        assert psw_obj.check(self.psw1)

    def test_create_lh1(self):
        psw_obj = passwd.Luohua1HashAlgorithm.create(self.uid, self.psw1)
        assert psw_obj.check(self.psw1)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
