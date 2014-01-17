#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 管理工具 / 系统安装 / 包
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
        'init_sysop_role',
        'init_sysop_user',
        ]

from ...auth.user import User
from ...auth.role import Role, OMNI_CAP
from ...auth.passwd import new_password

SYSOP_ROLE_ID = 'root'
SYSOP_UID = 'SYSOP'


def init_sysop_role():
    if Role.fetch(SYSOP_ROLE_ID) is not None:
        return False

    sysop_role = Role()
    sysop_role['id'] = SYSOP_ROLE_ID
    sysop_role['name'] = 'SYSOP'
    sysop_role['caps'] = set(OMNI_CAP)
    sysop_role.save()

    return True


def init_sysop_user(email, psw):
    if User.fetch(SYSOP_UID) is not None:
        return False

    sysop = User()
    sysop['id'] = SYSOP_UID
    sysop['password'] = new_password(psw)
    sysop['alias'] = ''
    sysop['email'] = email
    sysop['roles'] = set(SYSOP_ROLE_ID)
    sysop['xattr'] = {}
    sysop.save()

    return True


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
