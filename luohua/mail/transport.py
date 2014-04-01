#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 电子邮件 / 传输组件
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
        'transport_manager',
        ]

import os

import envelopes

from weiyu.registry.provider import request as regrequest


class MailTransport(object):
    def __init__(self, cfg):
        self._conn = envelopes.SMTP(
                cfg['host'],
                cfg['port'],
                cfg['login'],
                cfg['password'],
                cfg['tls'],
                cfg['timeout'],
                )

    def send(self, mail):
        return self._conn.send(mail)


class MailTransportManager(object):
    def __init__(self):
        # 取邮件服务器配置
        reg = self._reg = regrequest('luohua.mail')
        servers = self._servers = reg['servers']
        transports = self._transports = {}

        # 为各个服务器初始化 transport
        for server_name, server_cfg in servers.items():
            transports[server_name] = MailTransport(server_cfg)

    def get_transport(self, name):
        return self._transports[name]


if os.environ.get('_IN_SPHINX_DOC_BUILD', None) != 'true':
    transport_manager = MailTransportManager()
else:
    # fake for autodoc
    transport_manager = None


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
