#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 测试套件 / 数据结构 / 虚文件
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

from luohua.datastructures import vfile


class TestVFile(Case):
    @classmethod
    def setup_class(cls):
        cls.vfile_id = 123454321
        cls.owner_id = 42
        cls.ctime = 1329493828  # 这个其实是微雨 repo 的初始提交时间
        cls.topic = 'Test topic 测试话题 ざわざわ'
        cls.content = '这是测试内容。\n有换行，显得比较真实\n'
        cls.extras = {
                'a': 1,
                'b': True,
                }

        cls.file_1 = vfile.VFile(
                cls.vfile_id,
                cls.owner_id,
                cls.ctime,
                cls.topic,
                cls.content,
                cls.extras,
                )

    @classmethod
    def teardown_class(cls):
        pass

    def test_ctor(self):
        vf = self.file_1

        assert vf.id == self.vfile_id
        assert vf.owner == self.owner_id
        assert vf.ctime == self.ctime
        assert vf.topic == self.topic
        assert vf.content == self.content
        assert vf.extras == self.extras


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
