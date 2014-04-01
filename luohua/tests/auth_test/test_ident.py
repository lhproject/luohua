#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 测试套件 / 认证 / 实名记录
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

import six
from nose.tools import assert_raises

from ..utils import Case

from luohua.auth import ident


class TestIDNumber(Case):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_ID_NUMBER_TYPES(self):
        assert ident.ID_NUMBER_TYPE_LAST6 == 0

        assert isinstance(ident.ID_NUMBER_TYPES, frozenset)

    def test_validate_typeck(self):
        # 类型
        assert_raises(ValueError, ident.validate_id_number, 0, b'123456')
        assert_raises(ValueError, ident.validate_id_number, 0, 123456)

        # 未知身份信息类型
        assert_raises(ValueError, ident.validate_id_number, 1000, b'12312312')

    def test_validate_type_LAST6(self):
        # 身份证后六位
        typ = ident.ID_NUMBER_TYPE_LAST6

        # 验证成功
        assert ident.validate_id_number(typ, '123456') is None
        assert ident.validate_id_number(typ, '12345X') is None

        # 验证失败
        # 长度不正确
        assert_raises(ValueError, ident.validate_id_number, typ, '12345')
        assert_raises(ValueError, ident.validate_id_number, typ, '1234567')
        # 前五位有非数字字符
        assert_raises(ValueError, ident.validate_id_number, typ, ' 12345')
        assert_raises(ValueError, ident.validate_id_number, typ, '1234X5')
        # 最后一位不是大写 X
        assert_raises(ValueError, ident.validate_id_number, typ, '12345a')
        assert_raises(ValueError, ident.validate_id_number, typ, '12345x')


class TestFrozenIdent(Case):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_v1_dec(self):
        obj = ident.FrozenIdent.fetch('1030513101')

        assert 'gender' in obj
        assert isinstance(obj['gender'], six.integer_types)
        assert obj['gender'] == 0

        assert 'id_number_type' in obj
        assert isinstance(obj['id_number_type'], six.integer_types)
        assert obj['id_number_type'] == 0

        assert 'id_number' in obj
        assert isinstance(obj['id_number'], six.text_type)
        assert obj['id_number'] == '12345X'

    def test_check_ident_constants(self):
        assert ident.IDENT_OK == 0
        assert ident.CHECK_IDENT_NOTFOUND == 1
        assert ident.CHECK_IDENT_INVALID_INPUT == 2
        assert ident.CHECK_IDENT_WRONG == 3

    def test_check_ident(self):
        # 成功检查
        assert ident.FrozenIdent.check_ident('1030513101', 0, '12345X') == 0
        assert ident.FrozenIdent.check_ident('1030512202', 0, '543210') == 0

        # 不存在的编号
        assert ident.FrozenIdent.check_ident('1030513102', 0, '12345X') == 1

        # 输入信息不合法
        assert ident.FrozenIdent.check_ident('1030513101', 1, '12345X') == 2
        assert ident.FrozenIdent.check_ident('1030513101', 0, '12345') == 2
        assert ident.FrozenIdent.check_ident('1030513101', 0, '12345x') == 2

        # 身份信息不匹配
        assert ident.FrozenIdent.check_ident('1030513101', 0, '543210') == 3


class TestIdent(Case):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_frozen_info(self):
        idnt = ident.Ident.fetch('1030512202')
        fidnt = idnt.frozen_info
        assert fidnt is not None

        # 引用 cache
        fidnt2 = idnt.frozen_info
        assert fidnt2 is fidnt

        # 对比 fixture 信息
        assert fidnt['id_number'] == '543210'

    def test_frozen_info_no_assoc(self):
        idnt = ident.Ident()

        try:
            idnt.frozen_info
        except AttributeError:
            pass
        else:
            assert False, 'access to frozen_info should raise AttributeError'


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
