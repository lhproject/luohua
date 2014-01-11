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

    def test_time_sequences(self):
        # 为了节约时间, 都挤在一个 case 里了
        dt1 = sequences.descending_ts()
        at1 = sequences.ascending_ts()
        td1 = sequences.time_descending()
        td1_2 = sequences.time_descending()
        ta1 = sequences.time_ascending()
        ta1_2 = sequences.time_ascending()
        tds1 = sequences.time_descending_suffixed()
        tas1 = sequences.time_ascending_suffixed()

        time.sleep(1)

        dt2 = sequences.descending_ts()
        at2 = sequences.ascending_ts()
        td2 = sequences.time_descending()
        ta2 = sequences.time_ascending()
        tds2 = sequences.time_descending_suffixed()
        tas2 = sequences.time_ascending_suffixed()

        # 返回类型
        assert isinstance(dt1, six.integer_types)
        assert isinstance(at1, six.integer_types)
        assert isinstance(td1, six.text_type)
        assert isinstance(ta1, six.text_type)
        assert isinstance(tds1, six.text_type)
        assert isinstance(tas1, six.text_type)

        # 不带随机后缀的确定性序列性质, 一般来讲相应的两条语句之间不会间隔 1
        # 秒以上
        assert td1 == td1_2
        assert ta1 == ta1_2

        # 顺序约定
        assert dt1 > dt2
        assert at1 < at2
        assert td1 > td2
        assert ta1 < ta2
        assert tds1 > tds2
        assert tas1 < tas2


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
