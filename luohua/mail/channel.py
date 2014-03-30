#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 电子邮件 / 邮件通道
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
        'channel_manager',
        ]

import envelopes

from weiyu.registry.provider import request as regrequest

from . import transport


class MailChannel(object):
    def __init__(self, cfg):
        self._server = cfg['server']
        self._addr = cfg['addr']
        self._name = cfg['name']
        self._title_prefix = cfg['title_prefix']

        self._from_addr_prepared = (self._addr, self._name, )

    def _do_send(self, mail):
        conn = transport.transport_manager.get_transport(self._server)
        return conn.send(mail)

    def get_envelope(self, to_addr, subject, body, is_html):
        subject = '{0} {1}'.format(self._title_prefix, subject)

        if is_html:
            return envelopes.Envelope(
                    to_addr=to_addr,
                    from_addr=self._from_addr_prepared,
                    subject=subject,
                    html_body=body,
                    charset='utf-8',
                    )
        else:
            return envelopes.Envelope(
                    to_addr=to_addr,
                    from_addr=self._from_addr_prepared,
                    subject=subject,
                    text_body=body,
                    charset='utf-8',
                    )

    def sendmail(self, to_addr, subject, body, is_html=False):
        mail = self.get_envelope(to_addr, subject, body, is_html)
        return self._do_send(mail)


class MailChannelManager(object):
    def __init__(self):
        # 取邮件通道配置
        reg = self._reg = regrequest('luohua.mail')
        channels_cfg = self._channels_cfg = reg['channels']
        channels = self._channels = {}

        # 初始化邮件通道
        for channel_name, channel_cfg in channels_cfg.items():
            channels[channel_name] = MailChannel(channel_cfg)

    def get_channel(self, name):
        return self._channels[name]


channel_manager = MailChannelManager()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
