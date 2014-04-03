#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 工具 / URL 处理
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

__all__ = [
        'get_api_info',
        'get_frontend_info',
        'get_url',
        'get_api_url',
        'get_frontend_url',
        'reverse_api_url',
        ]

import six
urlparse = six.moves.urllib.parse

from weiyu import registry
from weiyu.shortcuts import reverse_http

BRIDGE_CONF_REGISTRY = 'luohua.bridge'


def get_api_info():
    return registry.request(BRIDGE_CONF_REGISTRY)['api']


def get_frontend_info():
    return registry.request(BRIDGE_CONF_REGISTRY)['frontend']


def get_url(netloc, path, query, fragment, https=True):
    return urlparse.urlunsplit((
            'https' if https else 'http',
            netloc,
            path,
            query,
            fragment,
            ))


def get_api_url(path):
    info = get_api_info()
    return get_url(info['domain'], path, '', '', info['https'])


def get_frontend_url(path):
    info = get_frontend_info()
    return get_url(info['domain'], path, '', '', info['https'])


def reverse_api_url(endpoint, **kwargs):
    path = reverse_http(endpoint, **kwargs)
    return get_api_url(path)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
