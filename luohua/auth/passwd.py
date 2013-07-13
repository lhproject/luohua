#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 认证 / 密码
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

import abc
import hashlib

from ..utils.randomness import random_salt

_KBS_MAGIC = r'wwj&kcn4SMTHBBS MD5 p9w2d gen2rat8, //grin~~, 2001/5/7'
HASH_ALGORITHMS = {}


def hash_alg(thing):
    HASH_ALGORITHMS[thing.algorithm] = thing
    return thing


class Password(object):
    def __init__(self, uid, alghash):
        self.uid = uid
        algorithm, hash = alghash.split('$', 1)
        self.alg = HASH_ALGORITHMS[algorithm](uid, hash)

    def check(self, psw):
        return self.alg.check(psw)


class BaseHashAlgorithm(object):
    __metaclass__ = abc.ABCMeta

    # Hash 算法的内部名称.
    # 因为会出现在所有此算法生成的 hash 中, 所以需要尽量简洁, 2 到 4
    # 个字符为好.
    algorithm = ''

    # 此 hash 算法是否加盐.
    # 如果为 ``False``, 生成的 hash 字符串将没有 salt 段.
    salted = True

    def __init__(self, uid, hash):
        digest, salt = self.split_hash(hash)
        self.uid, self.digest, self.salt = uid, digest, salt

    def __unicode__(self):
        if self.salt is not None:
            return '%s$%s|%s' % (self.algorithm, self.salt, self.digest, )
        return '%s$%s' % (self.algorithm, self.digest, )

    def __str__(self):
        return unicode(self).encode('utf-8')

    def __repr__(self):
        return b"<HashAlgorithm '%s': %s>" % (self.algorithm, str(self), )

    @classmethod
    @abc.abstractmethod
    def split_hash(cls, hash):
        return hash, None

    def check(self, psw):
        return self.digest == self.make_hash(psw, self.salt)

    @abc.abstractmethod
    def make_hash(self, psw, salt):
        pass

    @classmethod
    def create(cls, uid, psw):
        # 16 个随机字母数字的盐够长了吧...
        new_salt = random_salt(16)

        # XXX KBS Hash 无视随机生成的盐, 而需要使用 UID (这也是这个密码类需要
        # 同时传入用户 ID 才能正常工作的唯一原因)! 所以 make_hash 目前只能是
        # 成员方法 (本来应该是个类方法的), 这里就不能直接用. 必须先用假 hash
        # 包一层. 这个 kludge 在 KBS hash 失去主流之后将被立即删除
        fake_psw = cls(uid, '|')
        new_hash = fake_psw.make_hash(psw, new_salt)

        # 为了兼容性... 只能引入多一个类变量了
        # 构造一个完整的 alghash 用来回传进 Password.__init__()
        # 来构造真正的返回对象
        if cls.salted:
            alghash = '%s$%s|%s' % (cls.algorithm, new_salt, new_hash, )
        else:
            alghash = '%s$%s' % (cls.algorithm, new_hash, )

        return Password(uid, alghash)


@hash_alg
class KBSHashAlgorithm(BaseHashAlgorithm):
    algorithm = 'kbs'
    salted = False

    @classmethod
    def split_hash(cls, hash):
        return hash, None

    def make_hash(self, psw, salt):
        s = ''.join([_KBS_MAGIC, psw, _KBS_MAGIC, self.uid]).encode('utf-8')
        return hashlib.md5(s).hexdigest()


@hash_alg
class Luohua1HashAlgorithm(BaseHashAlgorithm):
    algorithm = 'lh1'
    salted = True

    @classmethod
    def split_hash(self, hash):
        salt, dgst = hash.split('|', 1)
        return dgst, salt

    def make_hash(self, psw, salt):
        return hashlib.sha512(salt + psw.encode('utf-8')).hexdigest()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
