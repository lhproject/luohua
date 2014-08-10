#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 测试套件 / 测试本体 / 工具
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

import nose
from nose.tools import assert_raises

from ..utils import Case, expected_failure


@expected_failure
def i_will_fail():
    raise AssertionError('yeah')


@expected_failure
def i_will_pass():
    pass


@expected_failure('wait, what')
def i_will_pass_with_message():
    pass


class TestTestUtils(Case):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_expected_failure_normal(self):
        assert_raises(nose.SkipTest, i_will_fail)

    def test_expected_failure_xpass(self):
        try:
            i_will_pass()
        except AssertionError as e:
            assert e.message == 'unexpected test pass'
        except Exception as e2:
            assert False, 'should raise AssertionError, not %s' % type(e2)
        else:
            assert False, 'should raise AssertionError but did not'

    def test_expected_failure_xpass_message(self):
        try:
            i_will_pass_with_message()
        except AssertionError as e:
            assert e.message == 'wait, what'
            return

        assert False, 'go check the result of test_expected_failure_xpass'


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
