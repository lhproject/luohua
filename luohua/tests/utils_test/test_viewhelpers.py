#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 测试套件 / 工具 / 视图辅助函数
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

from ..utils import Case
from ..shortcuts import *

from luohua.utils import viewhelpers


class TestViewHelpers(Case):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_jsonreply(self):
        status, content, ctx = viewhelpers.jsonreply(r=0)
        assert status == 200
        assert content == {'r': 0, }
        assert ctx == {}

    def test_parse_form(self):
        class MockRequest(object):
            def __init__(self, form):
                self.form = form

        req = MockRequest({'a': 1, 'b': 2, 'c': 3, })

        assert () == viewhelpers.parse_form(req)
        assert (1, ) == viewhelpers.parse_form(req, 'a', )
        assert (2, 1, 3, ) == viewhelpers.parse_form(req, 'b', 'a', 'c', )
        assert (1, 3, 0, ) == viewhelpers.parse_form(
                req,
                'a', 'c', 'd',
                c=0, d=0,
                )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
