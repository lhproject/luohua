#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / Blob 公共模块 / 存储后端 / 原生 Riak
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


class RiakNativeBlobBackend(BlobBackend):
    def __init__(self):
        pass

    def put(self, data, **kwargs):
        # 存储一个新的 Blob 对象, 返回其 Blob ID
        raise NotImplementedError

    def meta(self, blob_id, **kwargs):
        # 获取 Blob 对象元数据
        raise NotImplementedError

    def get(self, blob_id, **kwargs):
        # 读取 Blob 对象
        raise NotImplementedError

    def multipart_init(self, **kwargs):
        # 初始化一个 multipart blob 上传会话, 返回一个上传 ID
        raise NotImplementedError

    def multipart_store(self, upload_id, part_seq, data, **kwargs):
        # 向一个 multipart blob 上传会话添加 part
        raise NotImplementedError

    def multipart_finish(self, upload_id, parts, **kwargs):
        # 完成一个 multipart blob 的上传, 返回 blob id
        raise NotImplementedError

    def multipart_abort(self, upload_id):
        # 终止一个 multipart blob 的上传, 销毁所有已上传的 part
        raise NotImplementedError

    def multipart_list(self, upload_id):
        # 获取一个 multipart blob 的 part 上传状态情况
        raise NotImplementedError


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
