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
        ]

from weiyu.rendering import render_hub


class MailTemplate(object):
    template_view = None
    template_type = None

    def __init__(self, ctx):
        assert self.template_view is not None
        assert self.template_type is not None

        self.ctx = ctx

    def get_subject(self):
        raise NotImplementedError

    def get_body(self):
        return render_hub.render_view(
                self.template_view,
                self.ctx,
                {},
                self.template_type,
                )


class MakoMailTemplate(object):
    template_type = 'mako'


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
