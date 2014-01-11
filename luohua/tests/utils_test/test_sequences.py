#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 测试套件 / 工具 / 序列生成
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

import time
import six

from ..utils import Case

from luohua.utils import sequences


class TestSequences(Case):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_time_ascending(self):
        id1 = sequences.time_ascending()
        time.sleep(1)
        id2 = sequences.time_ascending()
        assert isinstance(id1, six.text_type)
        assert id1 > id2

    def test_time_descending(self):
        id1 = sequences.time_descending()
        time.sleep(1)
        id2 = sequences.time_descending()
        assert isinstance(id1, six.text_type)
        assert id1 < id2


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
