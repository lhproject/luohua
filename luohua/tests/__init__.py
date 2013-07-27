#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 测试套件 / 包
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

import os

from weiyu.shortcuts import load_all

from . import fixtures

TEST_SUITE_PATH = os.path.realpath(os.path.split(__file__)[0])
REPO_PATH = os.path.abspath(os.path.join(TEST_SUITE_PATH, '../..'))


def setup_package():
    os.chdir(REPO_PATH)

    # 这里是 Travis CI 么?
    # 根据 http://about.travis-ci.org/docs/user/ci-environment/
    # 因为这个环境变量名字最长所以用了...
    # 这是怕不小心在本机设置导致用错配置文件, 不是恶趣味!
    if os.environ.get('HAS_JOSH_K_SEAL_OF_APPROVAL', None) == 'true':
        conf = 'conf.for-travis.yml'
    else:
        conf = 'conf.yml'

    load_all(conf_path=os.path.join(REPO_PATH, conf))

    # 设置数据库
    fixtures.users_setup()


def teardown_package():
    # 还原数据库状态
    fixtures.users_teardown()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
