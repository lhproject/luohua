#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 任务队列 / 邮件发送
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

from __future__ import absolute_import, unicode_literals

import time

from . import celery
from ..utils import urls


@celery.jsontask
def send_ident_verify_mail_mail(number):
    # auth.ident 引用了这个模块, 所以不能在模块级加载, 会循环依赖的
    from ..auth import ident
    from ..auth import user

    curtime = int(time.time())

    # 取激活码
    ident_obj = ident.Ident.fetch(number)
    if ident_obj.activated:
        # 这个身份已经激活; 什么都不发送, 抛异常
        raise ValueError('this ident already activated: {0}'.format(number))

    to_addr = ident_obj['email']
    ak = ident_obj['activation_key']

    # 取用户显示名称和 HTML 邮件喜好
    user_obj = user.User.find_by_ident(number)
    display_name = user_obj['display_name']
    html = user_obj.prefs['mail.html']

    # 构造激活 URL
    # 激活 URL 现在指向前端服务, 暂时需要手工拼接字符串. 不过 Mako 会处理 URL
    # 特殊字符转义的工作, 这里大可放心地操作.
    activation_url = urls.get_frontend_url('/verifymail/%s' % (ak, ))

    tmpl = ident.IdentVerifyMailMailTemplate({
            'display_name': display_name,
            'url': activation_url,
            'curtime': curtime,
            })

    # 发信
    return tmpl.send_to_channel('main', to_addr, html)


@celery.jsontask
def send_ident_mail_verified_mail(number):
    from ..auth import ident
    from ..auth import user

    curtime = int(time.time())

    ident_obj = ident.Ident.fetch(number)
    number = ident_obj['id']
    to_addr = ident_obj['email']

    if not ident_obj.activated:
        # 这个身份还没有激活, 抛异常
        raise ValueError('this ident not activated yet: {0}'.format(
                number,
                ))

    user_obj = user.User.find_by_ident(number)
    display_name = user_obj['display_name']
    html = user_obj.prefs['mail.html']

    tmpl = ident.IdentMailVerifiedMailTemplate({
            'display_name': display_name,
            'curtime': curtime,
            })

    return tmpl.send_to_channel('main', to_addr, html)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
