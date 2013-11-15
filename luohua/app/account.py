#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 应用 / 账户
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

from weiyu.shortcuts import *
from weiyu.utils.decorators import only_methods

from ..auth.user import User
from ..utils.viewhelpers import jsonreply, parse_form


@http
@jsonview
def account_stat_v1_view(request):
    raise NotImplementedError


@http
@jsonview
def account_creat_v1_view(request):
    raise NotImplementedError


@http
@jsonview
def account_fcntl_v1_view(request):
    raise NotImplementedError


@http
@jsonview
def account_unlink_v1_view(request):
    raise NotImplementedError


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
