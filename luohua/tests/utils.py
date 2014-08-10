#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 测试套件 / 工具
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

import functools
import types

import nose


class Case(object):
    '''测试用例类。

    本类不从 ``unittest.TestCase`` 继承，主要是因为这样可以利用 ``nose``
    的扩展功能。

    '''

    # placeholder for future enhancements
    pass


def expected_failure(maybe_fail_msg=None):
    '''标记一个测试用例为应当失败.

    若被标记的测试失败, 将显示为跳过; 若成功, 则报告失败. 失败提示信息可以
    通过 ``fail_msg`` 参数指定.

    '''

    # 基于 http://stackoverflow.com/a/9615578/596531
    def _decorator_(msg, fn):
        @functools.wraps(fn)
        def _expected_failure_test(*args, **kwargs):
            try:
                fn(*args, **kwargs)
            except Exception:
                raise nose.SkipTest
            else:
                raised_msg = 'unexpected test pass' if msg is None else msg
                raise AssertionError(raised_msg)

        return _expected_failure_test

    # 方便使用, 如果用 ``@expected_failure`` 形式 (不加括号) 调用的话让它的
    # 行为与 ``@expected_failure()`` 一致
    if callable(maybe_fail_msg):
        # 这种情况下 maybe_fail_msg 实际上是被修饰的函数
        return _decorator_(None, maybe_fail_msg)

    # 否则就是报告失败的消息串
    return functools.partial(_decorator_, maybe_fail_msg)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
