#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 应用 / 会话管理模块 / 会话 token
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

__all__ = [
        'new_token_string',
        'query_token',
        'allocate_token',
        'request_token',
        'revoke_token',
        ]

import time

from weiyu.db import db_hub

from ...auth import audit
from ...utils import randomness

SESSION_TOKENS_STORAGE_ID = 'luohua.app.session.tokens'
TOKEN_STRING_LENGTH = 64
TOKENS_HASH_KEY = 'hash:tokens'
TOKEN_KEY_FORMAT = 'token:{typ}:{uid}:{addr}'

_CLIENT_CACHE = []


def _get_redis():
    '''获取 StrictRedis 客户端对象.'''

    # XXX 这一段的形式跟 rt.pubsub 的相应部分几乎一样... 该重构
    try:
        return _CLIENT_CACHE[0]
    except IndexError:
        pass

    client = db_hub.get_storage(SESSION_TOKENS_STORAGE_ID).raw()
    _CLIENT_CACHE.append(client)
    return client


def _get_token_hash_key(typ, remote_addr, uid):
    return TOKEN_KEY_FORMAT.format(typ=typ, uid=uid, addr=remote_addr)


def new_token_string():
    '''生成一个随机 token 字符串.'''

    return randomness.fixed_length_b64(TOKEN_STRING_LENGTH)


def query_token(token):
    '''返回指定 token 的信息.'''

    return _get_redis().hgetall(token) or None


def allocate_token(request, typ, uid):
    '''为指定用户新建一个给定类型的 token.'''

    curtime = int(time.time())

    token = new_token_string()
    hash_key = _get_token_hash_key(typ, request.remote_addr, uid)
    token_data = {
            'type': typ,
            'ctime': curtime,
            'remote_addr': request.remote_addr,
            'uid': uid,
            }

    conn = _get_redis()
    with conn.pipeline() as pipe:
        # 记录 token
        pipe.hmset(token, token_data)

        # 设置 (IP, UID)-token 映射
        pipe.hset(TOKENS_HASH_KEY, hash_key, token)

        pipe.execute()

    # 记录审计事件
    record = AllocateTokenAction(request, token=token, token_data=token_data)
    record.save()

    return token


def request_token(request, typ, uid):
    '''根据远端 IP 地址和 UID 请求一个给定类型的 token;
    如原先不存在, 则生成一个 token 并返回.

    '''

    hash_key = _get_token_hash_key(typ, request.remote_addr, uid)

    # 记录审计事件
    record = RequestTokenAction(request, type=typ, uid=uid)
    record.save()

    # 取 token
    conn = _get_redis()
    # 因为 allocate_token() 里使用了 pipeline,
    # 所以这里 token 的记录和映射的更新过程是原子的, 直接取就好了
    maybe_token = conn.hget(TOKENS_HASH_KEY, hash_key)
    if maybe_token is not None:
        # 已经有一个此 IP / UID 对应的 token, 返回
        return maybe_token

    return allocate_token(request, typ, uid)


def revoke_token(request, typ, uid, token):
    '''销毁一个给定用户创建的给定类型的 token.'''

    conn = _get_redis()
    token_data = query_token(token)

    # 验证权限
    # TODO: 让某角色的用户可以代替其他用户删除他们的 token?
    if token_data['uid'] != uid:
        # 操作用户不匹配
        record = RevokeTokenFailedAction(
                request,
                token=token,
                token_data=token_data,
                type=typ,
                uid=uid,
                )
        record.save()
        return False

    # 验证类型是否匹配
    if token_data['type'] != typ:
        # 欲删除 token 类型不匹配
        record = RevokeTokenFailedAction(
            request,
            token=token,
            token_data=token_data,
            type=typ,
            uid=uid,
            )
        record.save()
        return False

    remote_addr = token_data['remote_addr']
    hash_key = _get_token_hash_key(typ, remote_addr, uid)

    # 记录审计事件
    record = RevokeTokenAction(
            request,
            token=token,
            token_data=token_data,
            type=typ,
            uid=uid,
            )
    record.save()

    with conn.pipeline() as pipe:
        pipe.delete(token)
        pipe.hdel(TOKENS_HASH_KEY, hash_key)
        pipe.execute()

    return True


# 审计事件
class BaseSessionTokenAction(audit.BaseAuditedAction):
    MODULE_NAME = 'luohua.app.session.tokens'


class RequestTokenAction(BaseSessionTokenAction):
    ACTION_TYPE = 'request'

    @classmethod
    def _check_params_spec(cls, params):
        assert 'type' in params
        assert 'uid' in params


class AllocateTokenAction(BaseSessionTokenAction):
    ACTION_TYPE = 'allocate'

    @classmethod
    def _check_params_spec(cls, params):
        assert 'token' in params
        assert 'token_data' in params


class RevokeTokenAction(BaseSessionTokenAction):
    ACTION_TYPE = 'revoke'

    @classmethod
    def _check_params_spec(cls, params):
        assert 'token' in params
        assert 'token_data' in params
        assert 'type' in params
        assert 'uid' in params


class RevokeTokenFailedAction(BaseSessionTokenAction):
    ACTION_TYPE = 'revoke_fail'

    @classmethod
    def _check_params_spec(cls, params):
        assert 'token' in params
        assert 'token_data' in params
        assert 'type' in params
        assert 'uid' in params


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
