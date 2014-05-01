#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 测试套件 / 工具 / URL 处理
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

from nose.tools import assert_raises

from ..utils import Case

from weiyu import registry
from luohua.utils import urls


class TestURLs(Case):
    @classmethod
    def setup_class(cls):
        cls._old_bridge_cfg = registry._registries['luohua.bridge']
        registry._registries['luohua.bridge'] = {
                'api': {
                    'domain': 'api.example.com',
                    'https': True,
                    },
                'frontend': {
                    'domain': 'example.com',
                    'https': False,
                    },
                }

    @classmethod
    def teardown_class(cls):
        registry._registries['luohua.bridge'] = cls._old_bridge_cfg

    def test_get_api_info(self):
        info = urls.get_api_info()
        assert info == {'domain': 'api.example.com', 'https': True, }

    def test_get_frontend_domain(self):
        info = urls.get_frontend_info()
        assert info == {'domain': 'example.com', 'https': False, }

    def test_get_url(self):
        url1 = urls.get_url('abc.com', 'a/b', '', '')
        url1b = urls.get_url('abc.com', 'a/b', '', '', https=False)
        url2 = urls.get_url('abc.com', '/a/b', '', '')
        url3 = urls.get_url('abc.com', 'a/b/', '', '')
        url4 = urls.get_url('abc.com', 'a/b/', 'abc=123', '')
        url5 = urls.get_url('abc.com', 'a/b/', '', '!/foo')
        url6 = urls.get_url('abc.com', 'a/b/', 'abc=123', '!/foo')

        assert url1 == 'https://abc.com/a/b'
        assert url1b == 'http://abc.com/a/b'
        assert url2 == 'https://abc.com/a/b'
        assert url3 == 'https://abc.com/a/b/'
        assert url4 == 'https://abc.com/a/b/?abc=123'
        assert url5 == 'https://abc.com/a/b/#!/foo'
        assert url6 == 'https://abc.com/a/b/?abc=123#!/foo'

    def test_get_api_url(self):
        assert urls.get_api_url('a/b') == 'https://api.example.com/a/b'
        assert urls.get_api_url('/a/b') == 'https://api.example.com/a/b'
        assert urls.get_api_url('a/b/') == 'https://api.example.com/a/b/'

    def test_get_frontend_url(self):
        assert urls.get_frontend_url('a/b') == 'http://example.com/a/b'
        assert urls.get_frontend_url('/a/b') == 'http://example.com/a/b'
        assert urls.get_frontend_url('a/b/') == 'http://example.com/a/b/'

    def test_reverse_api_url(self):
        url1 = urls.reverse_api_url('api:vfile-creat-v1')
        assert url1 == 'https://api.example.com/v1/vf/creat/'

    def test_reverse_api_url_params(self):
        url2 = urls.reverse_api_url(
                'api:vpool-stat-v1',
                vtpid='123',
                )
        assert url2 == 'https://api.example.com/v1/vtp/123/stat/'

    def test_reverse_api_url_exc_behavior(self):
        assert_raises(ValueError, urls.reverse_api_url, 'non-existent-ep')
        assert_raises(ValueError, urls.reverse_api_url, 'api:non-existent-ep')
        assert_raises(ValueError, urls.reverse_api_url, 'xyz:non-existent-ep')


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
