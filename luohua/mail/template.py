#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 电子邮件 / 邮件模板
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
        'MailTemplate',
        'MakoMailTemplate',
        ]

from weiyu.rendering import render_hub
from weiyu.rendering.base import RenderContext

from .channel import channel_manager


class MailTemplate(object):
    template_path = None
    template_type = None
    is_html = None

    def __init__(self, ctx):
        assert self.template_path is not None
        assert self.template_type is not None
        assert self.is_html is not None

        self.ctx = ctx

    def get_subject(self):
        raise NotImplementedError

    def get_body(self):
        tmpl = render_hub.get_template(
                self.template_type,
                self.template_path,
                )

        return tmpl.render(self.ctx, RenderContext())[0]

    def send_to_channel(self, channel_name, to_addr):
        ch = channel_manager.get_channel(channel_name)
        return ch.send_from_template(to_addr, self)


class MakoMailTemplate(MailTemplate):
    template_type = 'mako'


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
