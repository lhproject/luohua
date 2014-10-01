#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / Blob 公共模块 / 存储后端 / 原生 Riak / Blob 对象
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

from weiyu.db import db_hub
from weiyu.db.mapper.base import Document
from weiyu.helpers.metaprogramming import classproperty
from weiyu.helpers.misc import smartbytes

from ....auth import user
from ....utils import sequences

BLOB_STRUCT_ID = 'luohua.blob.riaknative'
BLOB_METADATA_STRUCT_ID = 'luohua.blob.riaknative._meta'

BLOB_CTIME_IDX = 'ctime_int'
BLOB_OWNER_IDX = 'owner_bin'
BLOB_IS_PARTIAL_IDX = 'partial_int'

BLOB_FLAG_PARTIAL = 0x01
BLOB_FLAG_MULTIPART = 0x02


def make_blob_flags_int(partial, multipart):
    '''生成 blob flag 整数.'''

    flags = 0
    if partial:
        flags |= BLOB_FLAG_PARTIAL
    if multipart:
        flags |= BLOB_FLAG_MULTIPART

    return flags


def parse_blob_flags_int(flags):
    '''解析 blob flag 整数.'''

    return {
            'partial': flags & BLOB_FLAG_PARTIAL != 0,
            'multipart': flags & BLOB_FLAG_MULTIPART != 0,
            }


class RiakBlobMetadata(Document):
    '''Blob 元数据.

    因为该数据并非作为底层 Riak 对象的本体存在, 而是以元数据形式附着在实际
    blob 数据上, 所以本类并不直接参与数据库操作, 从而没有继承
    ``RiakDocument``.

    '''

    struct_id = BLOB_METADATA_STRUCT_ID

    @classmethod
    def decode_from_obj(cls, obj, version=None):
        '''从一个表示 blob 的 Riak 对象中解出元数据.'''

        # 处理 _V 字段
        # 因为解码过程显然并不关心 _V 字段内容, 所以直接处理出整数类型的版本,
        # 然后直接传入框架, 不修改原数据结构, 就能省掉一些内存访问了
        # NOTE: 这里取出的是 _V 或 _v 字段, 显然是因为 HTTP 协议下头部名称
        # 大小写不敏感, 而 usermeta 是作为头部传回的...
        meta_dict = obj.usermeta

        try:
            version = meta_dict[b'_V']
        except KeyError:
            version = meta_dict[b'_v']
            del meta_dict[b'_v']

        version = int(version)

        return cls.decode(meta_dict, version)

    @classmethod
    def encode_for_blob(cls, blob, version=None):
        '''为一个 blob 对象编码元数据使其能够直接入库.'''

        ret = cls.encode(blob, version)

        # 处理 _V 字段
        version = ret['_V']
        del ret['_V']
        ret[b'_V'] = smartbytes(str(version))

        return ret


@RiakBlobMetadata.decoder(1)
def blob_metadata_dec_v1(obj):
    flags = int(obj['flags'].decode('utf-8'))
    parsed_flags = parse_blob_flags_int(flags)

    result = {
        'filename': obj['filename'].decode('utf-8'),
        'ctime': int(obj['ctime'].decode('utf-8')) / 1000000.0,
        'uid': obj['uid'].decode('utf-8'),
    }

    result.update(parsed_flags)
    return result


@RiakBlobMetadata.encoder(1)
def blob_metadata_enc_v1(blob):
    flags = make_blob_flags_int(blob.is_partial, blob.is_multipart)

    return {
            b'filename': smartbytes(blob.filename),
            b'ctime': smartbytes(str(int(blob.ctime * 1000000))),
            b'uid': smartbytes(blob.owner_uid),
            b'flags': smartbytes(str(flags)),
            }


def new_blob_id():
    '''新建一个 Blob ID.'''

    return 'bb' + sequences.time_descending_short_suffixed()


class RiakBlob(object):
    '''使用 Riak 后端存储的 blob.'''

    struct_id = BLOB_STRUCT_ID

    def __init__(
            self,
            blob_id=None,
            data=None,
            filename=None,
            content_type=None,
            ctime=None,
            owner_uid=None,
            is_partial=False,
            is_multipart=False,
            ):
        # 缓存的所有者对象
        self._owner, self._is_owner_fresh = None, False

        if blob_id is None:
            blob_id_to_use = new_blob_id()
            with self.storage as conn:
                self._rawobj = conn.new(
                        key=blob_id_to_use,
                        data=data,
                        content_type=content_type,
                        )

            self._blob_id = blob_id_to_use
            self.filename = filename
            self.ctime = ctime
            self._owner_uid = owner_uid
            self.is_partial = is_partial
            self.is_multipart = is_multipart
        else:
            with self.storage as conn:
                obj = self._rawobj = conn.get(blob_id)
            metadata = RiakBlobMetadata.decode_from_obj(obj)

            self._blob_id = blob_id
            self.filename = metadata['filename']
            self.ctime = metadata['ctime']
            self._owner_uid = metadata['uid']
            self.is_partial = metadata['partial']
            self.is_multipart = metadata['multipart']

    @classproperty
    def storage(cls):
        '''``Document``-like interface for accessing underlying database.'''

        return db_hub.get_storage(cls.struct_id)

    @property
    def blob_id(self):
        return self._blob_id

    @property
    def data(self):
        return self._rawobj.encoded_data

    @data.setter
    def data(self, value):
        if not isinstance(value, bytes):
            raise TypeError('blob data must be bytes')
        self._rawobj.encoded_data = value

    @property
    def content_type(self):
        return self._rawobj.content_type

    @content_type.setter
    def content_type(self, value):
        self._rawobj.content_type = smartbytes(value)

    @property
    def owner(self):
        if self._is_owner_fresh:
            return self._owner

        owner = self._owner = user.User.fetch(self._owner_uid)
        self._is_owner_fresh = True
        return owner

    @property
    def owner_uid(self):
        return self._owner_uid

    @owner_uid.setter
    def owner_uid(self, value):
        # 清空可能缓存的上一个用户对象
        # NOTE: 这几个赋值显然不是线程安全的 (可自行反汇编字节码验证), 是否
        # 需要加锁待考
        self._owner, self._is_owner_fresh = None, False
        self._owner_uid = value

    def get_encoded_metadata(self):
        return RiakBlobMetadata.encode_for_blob(self)

    def save(self):
        # Riak 最佳实践: 写入之前先取回对象的最新版本 (主要是为了 vclock)
        # 但对于体积相对巨大的 blob 对象而言这样做真的合适?

        encoded_metadata = self.get_encoded_metadata()
        self._rawobj.usermeta = encoded_metadata

        self._rawobj.store()

    def purge(self):
        self._rawobj.reload()
        self._rawobj.delete()



# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
