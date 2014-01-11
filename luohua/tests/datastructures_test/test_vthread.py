#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 测试套件 / 数据结构 / 虚线索
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

import copy

from nose.tools import assert_raises

from ..utils import Case
from ..shortcuts import *

from luohua.datastructures import vthread


class TestVThreadTree(Case):
    @classmethod
    def setup_class(cls):
        t0 = [A]
        t1 = [
                A,
                [B, D, ],
                [C, E, J, ],
                [F, G, H, ],
                [I, ],
                [K, L, ],
                ]

        cls.thread_0 = vthread.VThreadTree(t0)
        cls.thread_1 = vthread.VThreadTree(t1)

        # 单独给插入回复测试用, 因为会变
        cls.thread_2 = vthread.VThreadTree(copy.deepcopy(t1))

    @classmethod
    def teardown_class(cls):
        pass

    def test_root(self):
        assert self.thread_1.root == 'A'

    def test_lengths(self):
        assert len(self.thread_0) == 1
        assert self.thread_0.num_direct_children() == 0

        assert len(self.thread_1) == 12
        assert self.thread_1.num_direct_children() == 5

    def test_contains(self):
        assert A in self.thread_1
        assert Z not in self.thread_1

    def test_flatten(self):
        assert 'A' == ''.join(self.thread_0.iter())
        assert 'ABCFIK' == ''.join(self.thread_1.iter())

        assert 'A' == ''.join(self.thread_0.iter_time_order())
        assert 'ABCDEFGHIJKL' == ''.join(self.thread_1.iter_time_order())

    def test_pagination(self):
        # 总页数计算
        assert self.thread_0.num_pages(5) == 1
        assert self.thread_1.num_pages(5) == 3
        assert self.thread_1.num_pages(6) == 2
        assert self.thread_1.num_pages(30) == 1

        # 分页
        seq_0_0 = ''.join(self.thread_0.iter_paginated(5, 0))
        seq_0_1 = ''.join(self.thread_0.iter_paginated(5, 1))

        seq_1_0 = ''.join(self.thread_1.iter_paginated(5, 0))
        seq_1_1 = ''.join(self.thread_1.iter_paginated(5, 1))
        seq_1_2 = ''.join(self.thread_1.iter_paginated(5, 2))
        seq_1_100 = ''.join(self.thread_1.iter_paginated(5, 100))

        assert seq_0_0 == 'A'
        assert seq_0_1 == ''
        assert seq_1_0 == 'ABCDE'
        assert seq_1_1 == 'FGHIJ'
        assert seq_1_2 == 'KL'
        assert seq_1_100 == ''

    def test_append_to(self):
        self.thread_2.append_to(None, M)
        self.thread_2.append_to(C, N)
        assert_raises(ValueError, self.thread_2.append_to, D, O)

        assert 'ABCFIKM' == ''.join(self.thread_2.iter())
        assert 'CEJN' == ''.join(self.thread_2.tree[2])


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
