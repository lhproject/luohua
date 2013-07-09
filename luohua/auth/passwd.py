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


def hash_alg(name):
    def _decorator_(thing):
        HASH_ALGORITHMS[name] = thing
        return thing
    return _decorator_


class Password(object):
    def __init__(self, uid, hash):
        self.uid = uid
        algorithm, digest = hash.split('$', 1)
        self.alg = HASH_ALGORITHMS[algorithm](uid, digest)

    def check(self, psw):
        return self.alg.check(psw)


class BaseHashAlgorithm(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, uid, hash):
        pass

    @abc.abstractmethod
    def check(self, psw):
        pass

    @abc.abstractmethod
    def make_hash(self, psw, salt=None):
        pass


@hash_alg('kbs')
class KBSHashAlgorithm(BaseHashAlgorithm):
    def __init__(self, uid, digest):
        self.uid = uid
        self.digest = digest

    def check(self, psw):
        return self.digest == self.make_hash(psw, None)

    def make_hash(self, psw, salt=None):
        s = ''.join([_KBS_MAGIC, psw, _KBS_MAGIC, self.uid]).encode('utf-8')
        return hashlib.md5(s).hexdigest()


@hash_alg('lh1')
class Luohua1HashAlgorithm(BaseHashAlgorithm):
    def __init__(self, uid, digest):
        salt, dgst = digest.split('|', 1)
        self.uid, self.salt, self.digest = uid, salt, dgst

    def check(self, psw):
        return self.digest == self.make_hash(psw, self.salt)

    def make_hash(self, psw, salt=None):
        salt = salt or random_salt(16)
        return hashlib.sha512(salt + psw.encode('utf-8')).hexdigest()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
