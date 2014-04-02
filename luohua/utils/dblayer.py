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


class MultipleObjectsError(ValueError):
    '''2i 查询对最多只期待 1 个结果的查询返回了多于 1 个的结果.'''

    pass


class RiakDocument(Document):
    '''存储于 Riak 的对象公共包装.

    '''

    # 框架需要, 跳过 struct_id 非 None 检查
    _abstract_ = True

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

    def __repr__(self):
        return '<RiakDocument {1} raw={2}>'.format(
                self.struct_id,
                super(RiakDocument, self).__repr__(),
                repr(self._rawobj),
                )

    @classmethod
    def _from_obj(cls, obj):
        '''从数据库对象生成 Python 对象. 这是内部方法, 外界不应直接使用.'''

        return cls(obj.data, obj.key, obj) if obj.exists else None

    @classmethod
    def _do_fetch_by_index(cls, idx, key):
        with cls.storage as conn:
            page = conn.get_index(smartbytes(idx), smartbytes(key))
            for obj_key in page.results:
                obj = conn.get(obj_key)
                yield cls._from_obj(obj)

    @classmethod
    def _do_fetch_one_by_index(cls, idx, key):
        result = list(cls._do_fetch_by_index(idx, key))

        if result:
            if len(result) > 1:
                raise MultipleObjectsError(
                        '>1 record returned from idx={0} key={1}'.format(
                            repr(idx),
                            repr(key),
                            ))
            return result[0]

        return None

    @classmethod
    def _do_fetch_range_by_index(cls, idx, start, end):
        with cls.storage as conn:
            page = conn.get_index(smartbytes(idx), start, end)
            for obj_key in page.results:
                obj = conn.get(obj_key)
                yield cls._from_obj(obj)

    @classmethod
    def fetch(cls, key):
        '''按文档 ID 获取一个被包装对象.

        :param key: 要获取对象的文档 ID.
        :type key: :data:`six.text_type`
        :return: 指定的对象; 如果指定对象不存在则返回 :const:`None`.
        :rtype: :class:`RiakDocument <luohua.utils.dblayer.RiakDocument>`
                或 :data:`types.NoneType`

        '''

        # XXX 这个方法不能叫 get, 因为那样会覆盖掉 dict 的 get 方法!
        with cls.storage as conn:
            obj = conn.get(key)
            return cls._from_obj(obj)

    @classmethod
    def fetch_multiple(cls, keys):
        '''按文档 ID 列表一次性获取多个被包装对象.

        :param keys: 要获取对象的文档 ID 列表.
        :type keys: list
        :return: 按顺序返回指定对象的迭代器.
        :rtype: :data:`types.GeneratorType`

        '''

        with cls.storage as conn:
            for key in keys:
                yield cls._from_obj(conn.get(key))

    @classmethod
    def find_all(cls):
        '''一次性获取所有被包装对象.

        :return: 按顺序返回对象的迭代器.
        :rtype: :data:`types.GeneratorType`

        '''

        with cls.storage as conn:
            for key in conn.get_keys():
                yield cls._from_obj(conn.get(key))

    @classmethod
    def fetch_fts(cls, expression):
        '''利用全文搜索索引查找符合条件的一个对象。

        如果没有符合条件的对象, 则抛 :exc:`KeyError` 异常;
        如果符合条件的对象多于一个, 则抛 :exc:`ValueError` 异常.

        :param expression: Riak 全文搜索查询表达式, 用法和
                :meth:`RiakBucket.search() <riak.bucket.RiakBucket.search>`
                一致. 需要自行 escape 处理.
        :type expression: :data:`six.text_type`
        :rtype: :class:`RiakDocument <luohua.utils.dblayer.RiakDocument>`

        '''

        with cls.storage as conn:
            # protobuf 协议要求查询字串必须是字节流, 所以编个码
            # HTTP 协议无所谓, unicode 或者 bytes 都可以
            result = conn.search(smartbytes(expression))

            num, docs = result['num_found'], result['docs']
            if num == 0:
                raise KeyError(expression)
            elif num > 1:
                raise ValueError(
                        'Multiple results returned for expression %s'
                        % repr(expression)
                        )

            # 拿出 ID, 生成对象返回
            key = docs[0]['id']
            return cls._from_obj(conn.get(key))

    def _do_sync_2i(self, obj):
        '''保存对象时同步 2i 索引.

        如果使用到 2i 索引, 请在子类设置 :attr:`uses_2i` 为 :const:`True`,
        并为此方法提供实现. 此方法应返回一个设置好的 :class:`RiakObject
        <riak.riak_object.RiakObject>` 对象.

        :param obj: 准备同步 2i 索引的 Riak 对象.
        :type obj: :class:`RiakObject <riak.riak_object.RiakObject>`
        :return: 设置好 2i 索引的 Riak 对象.
        :rtype: :class:`RiakObject <riak.riak_object.RiakObject>`

        '''

        return obj

    def save_to_conn(self, conn):
        '''使用给定的数据库连接保存对象到数据库.

        .. note::

            此方法主要是用于批量操作时减少一些多余的操作 (虽然 Riak
            的连接是没有状态的, 但仍然会造成大量多余的空函数调用),
            一般处理少量数据时建议使用 :meth:`.save` 方法以降低代码复杂度.

        :param conn: 欲使用的 Riak 连接.
        :type conn: :class:`RiakBucket <riak.bucket.RiakBucket>`
        :return: :const:`None`

        '''

        obj = self._rawobj if self._rawobj is not None else conn.new()
        obj.key, obj.data = self.get('id'), self.encode()

        # 如果有的话就同步 2i 索引
        if self.uses_2i:
            obj = self._do_sync_2i(obj)

        obj.store()

        # 刷新对象关联信息
        self['id'], self._rawobj = obj.key, obj

    def save(self):
        '''保存对象到数据库.

        .. note::

            此方法会请求一条新数据库连接进行工作. 如果需要进行批量数据库操作,
            建议自行在工作函数内使用 ``with SomeDocument.storage as conn:``
            获取一条连接, 并配合 :meth:`.save_to_conn` 重复利用该连接.

        :return: :const:`None`

        '''

        with self.storage as conn:
            return self.save_to_conn(conn)

    def purge(self):
        '''从数据库中彻底删除被包装对象.

        :return: :const:`None`

        '''

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
