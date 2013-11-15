#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 测试套件 / 应用 / 虚线索池
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

from weiyu.router import router_hub
from luohua.app.v1 import vpool


class TestVPoolViews(Case):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_view_presence_v1(self):
        # XXX 这里使用了微雨框架的实现细节
        http_views = router_hub._endpoints['http']

        assert 'vpool-stat-v1' in http_views
        assert 'vpool-getdents-v1' in http_views
        assert 'vpool-creat-v1' in http_views
        assert 'vpool-fcntl-v1' in http_views
        assert 'vpool-unlink-v1' in http_views


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
