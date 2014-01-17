#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 应用 / 统计数据模块 / 中间件
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

from __future__ import unicode_literals, division, print_function

import time

from weiyu.adapters import adapter_hub
from weiyu.helpers.misc import smartbytes


def get_req_prefixed_logger(request):
    # 调试目的, 只要不同请求不一样, 同一请求一样就行
    req_id = id(request)
    req_prefix = b'[%16x] ' % (req_id, )

    def _logger_print_(value, *args, **kwargs):
        return print(req_prefix + smartbytes(value), *args, **kwargs)
    return _logger_print_


@adapter_hub.declare_middleware('luohua.metrics')
class LHMetricsMiddleware(object):
    def do_pre(self, request):
        start_time = time.time()
        request._metrics_start_time = start_time

        log = get_req_prefixed_logger(request)

        log('Path=' + request.path)
        log('From=' + request.remote_addr)

        try:
            log('UA=' + request.env['HTTP_USER_AGENT'])
        except KeyError:
            log('UA n/a')

    def do_post(self, response):
        end_time = time.time()
        elapsed_time = end_time - response.request._metrics_start_time

        log = get_req_prefixed_logger(response.request)

        log('Status=%d' % (response.status, ))
        log('t=%.3fms' % (elapsed_time * 1000, ))


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
