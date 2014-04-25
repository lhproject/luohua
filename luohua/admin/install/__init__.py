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
        'init_default_roles',
        ]

from ...auth.user import User
from ...auth.role import Role, OMNI_CAP
from ...auth.passwd import new_password

from ...datastructures import vpool

SYSOP_ROLE_ID = 'root'
GLOBAL_VTPID = '0'


def init_sysop_role():
    if Role.fetch(SYSOP_ROLE_ID) is not None:
        return False

    sysop_role = Role()
    sysop_role['id'] = SYSOP_ROLE_ID
    sysop_role['name'] = 'SYSOP'
    sysop_role['caps'] = set(OMNI_CAP)
    sysop_role.save()

    return True


def init_default_roles():
    # 确保 initial 角色
    tmp1 = Role.fetch('initial')
    if tmp1 is not None:
        tmp1.purge()

    initial_role = Role()
    initial_role['id'] = 'initial'
    initial_role['name'] = '初始角色'
    initial_role['caps'] = {'user-login', 'vf-creat', }
    initial_role.save()

    # 确保 default 角色 (邮箱验证通过之后的默认权限)
    tmp2 = Role.fetch('default')
    if tmp2 is not None:
        tmp2.purge()

    default_role = Role()
    default_role['id'] = 'default'
    default_role['name'] = '默认用户角色'
    default_role['caps'] = {'vth-creat', }
    default_role.save()

    return True


def init_global_vpool():
    if vpool.VPool.fetch(GLOBAL_VTPID) is not None:
        return False

    vtp = vpool.VPool()
    vtp['id'] = GLOBAL_VTPID
    vtp['name'] = '全局虚线索池'
    vtp['natural'] = True
    vtp['xattr'] = {}
    vtp.save()

    return True


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
