#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 工具 / 视图辅助函数
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

__all__ = [
        'jsonreply',
        'parse_form',
        ]


def jsonreply(**kwargs):
    return 200, kwargs, {}


def parse_form(request, *args, **kwargs):
    '''从请求对象顺序解出表单参数成 tuple.

    支持将一些参数设置为可选, 这些参数的默认值用同名的命名参数方式传入.

    '''

    frm = request.form
    return tuple(
            frm[i] if i not in kwargs else frm.get(i, kwargs[i])
            for i in args
            )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
