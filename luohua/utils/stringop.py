#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 工具 / 字符串操作
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
        'escape_lucene',
        ]

import re

# 残酷的转义序列啊...
# 参见 http://lucene.apache.org/core/2_9_4/queryparsersyntax.html
LUCENE_SPECIALCHARS = r'\+|-|&&|\|\||!|\(|\)|\{|\}|\[|\]|\^|\"|~|\*|\?|:|\\'
LUCENE_SPECIALCHARS_RE = re.compile(LUCENE_SPECIALCHARS)


def _lucene_escaper_helper(match):
    return '\\' + match.group(0)


def escape_lucene(s):
    return LUCENE_SPECIALCHARS_RE.sub(_lucene_escaper_helper, s)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
