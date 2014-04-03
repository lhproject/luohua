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
from ..auth import ident
from ..utils import urls


@celery.jsontask
def send_ident_verify_mail(to_addr, number, html):
    curtime = int(time.time())

    # 取激活码
    ident_obj = ident.Ident.fetch(number)
    ak = ident_obj['activation_key']
    if ak == ident.ALREADY_ACTIVATED_KEY:
        # 这个身份已经激活; 什么都不发送, 抛异常
        raise ValueError('this ident already activated: {0}'.format(number))

    # 构造激活 URL
    activation_url = urls.reverse_api_url(
            'api:ident-activate-v1',
            activation_key=ak,
            )

    tmpl = ident.IdentVerifyMailMailTemplate({
            'url': activation_url,
            'curtime': curtime,
            })

    # 发信
    return tmpl.send_to_channel('main', to_addr, html)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
