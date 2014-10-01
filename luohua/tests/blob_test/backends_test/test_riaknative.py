#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 测试套件 / Blob 公共模块 / 存储后端 / 包
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

import time
import six
import mock

from ...utils import Case, expected_failure

from ....blob.backends.riaknative import blob as rn_blob


class TestRiakNativeBlobFlags(Case):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_blob_flags_round_trip(self):
        make_flags = rn_blob.make_blob_flags_int
        parse_flags = rn_blob.parse_blob_flags_int

        for partial in (False, True, ):
            for multipart in (False, True):
                flags_int = make_flags(partial, multipart)
                parsed_flags = parse_flags(flags_int)

                assert parsed_flags['partial'] == partial
                assert parsed_flags['multipart'] == multipart


class TestRiakNativeBlobMetadata(Case):
    @classmethod
    def setup_class(cls):
        class DummyBlob(object):
            def __init__(self):
                self.blob_id = 'bbfoobarbaz'
                self.data = 'hello world\n'
                self.filename = 'test中文.txt'
                self.content_type = 'text/plain'
                self.ctime = time.time()
                self.owner_uid = 'root'
                self.is_partial = False
                self.is_multipart = False

        cls.DummyBlob = DummyBlob

        cls.encode_for_blob = rn_blob.RiakBlobMetadata.encode_for_blob
        cls.decode_from_obj = rn_blob.RiakBlobMetadata.decode_from_obj

    @classmethod
    def teardown_class(cls):
        pass

    def test_encode_for_blob_v1(self):
        dummy_blob = self.DummyBlob()
        encoded_metadata = self.encode_for_blob(dummy_blob, 1)

        assert isinstance(encoded_metadata, dict)
        for k, v in six.iteritems(encoded_metadata):
            assert isinstance(k, six.binary_type), (
                'key %s not of six.binary_type' % repr(k)
                )
            assert isinstance(v, six.binary_type), (
                'value %s not of six.binary_type' % repr(k)
                )

        assert encoded_metadata['_V'] == b'1'
        assert encoded_metadata['filename'] == b'test中文.txt'
        # Python 3 的 int 能接受 str 也能接受 bytes 所以这里不用明确转换
        correctly_encoded_ctime = int(dummy_blob.ctime * 1000000)
        assert int(encoded_metadata['ctime']) == correctly_encoded_ctime
        assert encoded_metadata['uid'] == b'root'
        # hardcode 了 flags 的取值, 因为 flags 已经有测试覆盖了
        assert encoded_metadata['flags'] == b'0'

    def test_decode_from_obj_v1(self):
        class DummyRiakObjectWithMeta(object):
            def __init__(self, usermeta):
                self.usermeta = usermeta

        dummy_obj = DummyRiakObjectWithMeta({
                b'_V': b'1',
                b'filename': b'test中文.txt',
                b'ctime': b'1408467588673396',
                b'uid': b'root',
                b'flags': b'0',
                })

        metadata = self.decode_from_obj(dummy_obj, 1)

        assert isinstance(metadata, dict)
        assert isinstance(metadata['filename'], six.text_type)
        assert metadata['filename'] == 'test中文.txt'
        assert isinstance(metadata['ctime'], float)
        assert abs(metadata['ctime'] - 1408467588.673396) < 1e-6
        assert isinstance(metadata['uid'], six.text_type)
        assert metadata['uid'] == 'root'
        assert isinstance(metadata['partial'], bool)
        assert not metadata['partial']
        assert isinstance(metadata['multipart'], bool)
        assert not metadata['multipart']


class TestRiakNativeBlob(Case):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    def test_new_blob_id(self):
        ret = rn_blob.new_blob_id()
        assert isinstance(ret, six.text_type)
        assert ret[:2] == 'bb'

    def test_ctor_auto_blob_id(self):
        blob = rn_blob.RiakBlob()
        assert blob.blob_id is not None

    def test_roundtrip(self):
        # 创建一个 blob 并保存
        blob = rn_blob.RiakBlob()
        saved_blob_id = blob.blob_id
        saved_data = blob.data = b'12345678' * 131072  # 1MiB
        saved_filename = blob.filename = 'test_roundtrip.txt'
        saved_content_type = blob.content_type = 'text/plain'
        saved_ctime = blob.ctime = time.time()
        saved_owner_uid = blob.owner_uid = '0'
        saved_is_partial = blob.is_partial = False
        saved_is_multipart = blob.is_multipart = False
        blob.save()

        assert saved_blob_id == blob.blob_id
        del blob

        blob2 = rn_blob.RiakBlob(saved_blob_id)
        assert blob2.blob_id == saved_blob_id
        assert blob2.data == saved_data
        assert blob2.filename == saved_filename
        assert blob2.content_type == saved_content_type
        assert blob2.ctime - saved_ctime < 1e-6
        assert blob2.owner_uid == saved_owner_uid
        assert blob2.is_partial == saved_is_partial
        assert blob2.is_multipart == saved_is_multipart

        # 删除测试用 blob
        blob2.purge()


class TestRiakNative(Case):
    @classmethod
    def setup_class(cls):
        pass

    @classmethod
    def teardown_class(cls):
        pass

    @expected_failure
    def test_put(self):
        # TODO
        raise NotImplementedError

    @expected_failure
    def test_get(self):
        # TODO
        raise NotImplementedError

    @expected_failure
    def test_meta(self):
        # TODO
        raise NotImplementedError

    @expected_failure
    def test_purge(self):
        # TODO
        raise NotImplementedError

    @expected_failure
    def test_multipart(self):
        # TODO
        raise NotImplementedError


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
