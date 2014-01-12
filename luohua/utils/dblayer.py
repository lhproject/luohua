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

from weiyu.helpers.misc import smartbytes
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
    def _do_fetch_by_index(cls, idx, key):
        with cls.storage as conn:
            page = conn.get_index(idx, key)
            for obj_key in page.results:
                obj = conn.get(obj_key)
                yield cls._from_obj(obj)

    @classmethod
    def _do_fetch_range_by_index(cls, idx, start, end):
        with cls.storage as conn:
            page = conn.get_index(idx, start, end)
            for obj_key in page.results:
                obj = conn.get(obj_key)
                yield cls._from_obj(obj)

    @classmethod
    def fetch(cls, key):
        '''按文档 ID 获取一个被包装对象.'''

        # XXX 这个方法不能叫 get, 因为那样会覆盖掉 dict 的 get 方法!
        with cls.storage as conn:
            obj = conn.get(key)
            return cls._from_obj(obj)

    @classmethod
    def fetch_multiple(cls, keys):
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

    @classmethod
    def fetch_fts(cls, expression):
        '''利用全文搜索索引查找符合条件的一个对象。

        如果没有符合条件的对象, 则抛 :exc:`KeyError` 异常;
        如果符合条件的对象多于一个, 则抛 :exc:`ValueError` 异常.

        :param expression: Riak 全文搜索查询表达式. 需要自行 escape 处理.
        :type expression: :class:`six.text_type`
        :rtype: :class:`RiakDocument <luohua.utils.dblayer.RiakDocument>`

        '''

        with cls.storage as conn:
            r = conn.search(smartbytes(expression))

            num, docs = r['num_found'], r['docs']
            if num == 0:
                raise KeyError(expression)
            elif num > 1:
                raise ValueError(
                        'Multiple results returned for expression %s'
                        % repr(expression)
                        )

            # 拿出 ID, 生成对象返回
            rid = docs[0]['id']
            return cls._from_obj(conn.get(rid))

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
