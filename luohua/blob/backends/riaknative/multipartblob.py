#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / Blob 公共模块 / 存储后端 / 原生 Riak / 多部分 Blob 对象
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

from .. import BlobBackend
from ....utils import dblayer

BLOB_UPLOAD_SESSION_STRUCT_ID = 'luohua.blob.riaknative.upload'


class RiakBlobUploadSession(dblayer.RiakDocument):
    struct_id = BLOB_UPLOAD_SESSION_STRUCT_ID


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
