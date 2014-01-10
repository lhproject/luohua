#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 工具 / 数据库抽象层
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

from weiyu.db.mapper.base import Document


class RiakDocument(Document):
    '''存储于 Riak 的对象公共包装.

    '''

    # 是否使用到 2i 索引, 子类如果使用到 2i 需要把这里设置成 True,
    # 并实现 _do_sync_2i 方法
    uses_2i = False

    def __init__(self, data=None, key=None, rawobj=None):
        super(RiakDocument, self).__init__()

        if data is not None:
            self.update(self.decode(data))

        if key is not None:
            self['id'] = key

        self._rawobj = rawobj

    @classmethod
    def _from_obj(cls, obj):
        '''从数据库对象生成 Python 对象. 这是内部方法, 外界不应直接使用.'''

        return cls(obj.data, obj.key, obj) if obj.exists else None

    @classmethod
    def _do_fetch_by_index(
            cls,
            idx,
            key,
            max_results,
            continuation,
            continuation_callback=None,
            ):
        with cls.storage as conn:
            page = conn.get_index(
                    idx,
                    key,
                    max_results=max_results,
                    continuation=continuation,
                    )
            for vthid in page.results:
                obj = conn.get(vthid)
                yield cls._from_obj(obj)

            # XXX: 有时候需要同时回传 continuation, 只好先这么 hack 了
            # 有机会重构的话这个一定要解决掉
            if continuation_callback is not None:
                continuation_callback(
                        page.continuation
                        if page.has_next_page()
                        else ''
                        )

    @classmethod
    def get(cls, key):
        '''按文档 ID 获取一个被包装对象.'''

        with cls.storage as conn:
            obj = conn.get(key)
            return cls._from_obj(obj)

    @classmethod
    def get_multiple(cls, keys):
        '''按文档 ID 列表一次性获取多个被包装对象.'''

        with cls.storage as conn:
            for key in keys:
                yield cls._from_obj(conn.get(key))

    @classmethod
    def find_all(cls):
        '''一次性获取所有被包装对象.'''

        with cls.storage as conn:
            for key in conn.get_keys():
                yield cls._from_obj(conn.get(key))

    def _do_sync_2i(self, obj):
        '''保存对象时同步 2i 索引.

        如果使用到 2i 索引, 请在子类设置 ``have_2i`` 为 ``True``,
        并为此方法提供实现. 此方法应返回一个设置好的 RiakObject 对象.

        '''

        return obj

    def save(self):
        '''保存对象到数据库.'''

        with self.storage as conn:
            obj = self._rawobj if self._rawobj is not None else conn.new()
            obj.key, obj.data = self.get('id'), self.encode()

            # 如果有的话就同步 2i 索引
            if self.uses_2i:
                obj = self._do_sync_2i(obj)

            obj.store()

            # 刷新对象关联信息
            self['id'], self._rawobj = obj.key, obj

    def purge(self):
        '''从数据库中彻底删除被包装对象.'''

        with self.storage as conn:
            if self._rawobj is None:
                raise ValueError(
                        'not associated with a Riak object, thus not '
                        'purgeable'
                        )

            self._rawobj.delete()
            self._rawobj = None
            del self['id']


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
