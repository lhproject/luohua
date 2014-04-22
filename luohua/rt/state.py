#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 实时信道 / 会话状态
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
        'state_mgr',
        ]

import time

from weiyu.db import db_hub

from ..auth import user
from ..utils import randomness
from ..utils import sequences

from . import pubsub

RT_STATE_STORAGE_ID = 'luohua.rt.state'

LOGIN_DISABLED_KEY = 'rt:nologin'
RT_LOGIN_TOKEN_KEY_FMT = 'rt:login:{0}'
RT_LOGIN_TOKEN_TTL_SECS = 60
RT_SESSION_KEY_FMT = 'rt:sess:{0}'
USER_SESSIONS_KEY_FMT = 'rt:usersess:{0}'


def get_rt_login_token_key(sid):
    return RT_LOGIN_TOKEN_KEY_FMT.format(sid)


def get_rt_session_key(rt_sid):
    return RT_SESSION_KEY_FMT.format(rt_sid)


def get_user_sessions_key(uid):
    return USER_SESSIONS_KEY_FMT.format(uid)


def generate_rt_login_token():
    '''生成一个实时信道登陆 token 串.'''

    return randomness.fixed_length_b64(64)


class RTStateManager(object):
    '''实时信道全局状态组件.'''

    def __init__(self):
        # 这么写是为了防止在模块 import 时做出真正的初始化动作
        self._conn = None

    @property
    def conn(self):
        '''获取 Redis 连接.'''

        # 其实是又一种保留 Redis 对象的方法... rt.pubsub 和 app.session.tokens
        # 表示 "重构是什么可以吃吗?"
        if self._conn is not None:
            return self._conn

        conn = self._conn = db_hub.get_storage(RT_STATE_STORAGE_ID).raw()
        return conn

    def purge_state(self):
        '''清空所有实时会话.'''

        # 在清空期间不允许新的登陆, 清空之后这条记录也会消失所以登陆会自动开放
        self.conn.set(LOGIN_DISABLED_KEY, 1)

        # 强迫所有客户端断开连接
        pubsub.publish_global_event('force_disconnect')

        # 清 Redis 库
        self.conn.flushdb()

    def issue_rt_login_token(self, sid):
        '''根据会话 ID 发行一个实时信道登陆 token.'''

        token_key = get_rt_login_token_key(sid)
        new_token = generate_rt_login_token()

        # 用原子操作设置 token, 以防止多个来自相同 sid 的刷新请求产生的 token
        # 互相覆盖
        with self.conn.pipeline() as pipe:
            pipe.set(
                    token_key,
                    new_token,
                    ex=RT_LOGIN_TOKEN_TTL_SECS,
                    nx=True,
                    )
            pipe.get(token_key)
            results = pipe.execute()

        result_token_bytes = results[1]
        assert isinstance(result_token_bytes, bytes)
        result_token = result_token_bytes.decode('ascii')
        assert len(result_token) > 0

        return result_token

    def check_rt_login_token(self, sid, login_token):
        '''检查实时信道登陆 token 是否有效.'''

        token_key = get_rt_login_token_key(sid)
        maybe_token = self.conn.get(token_key)
        return maybe_token == login_token

    def do_rt_login(self, sid, user_obj, login_token):
        '''试图将携带指定实时信道登陆 token 的指定会话 ID 登陆进实时信道.

        如登陆成功, 将生成一个独立的实时会话 ID 并返回.

        '''

        curtime = int(time.time())
        conn = self.conn

        # 系统当前是否允许新登陆?
        if conn.get(LOGIN_DISABLED_KEY) is not None:
            # 全局设定为不允许, 直接失败
            return None

        # 验证 token
        if not self.check_rt_login_token(sid, login_token):
            # 验证不通过
            return None

        # 生成实时会话 ID, 简单记录下信息
        rt_sid, is_sid_ok = sequences.time_ascending_suffixed(curtime), False
        rt_session_key = get_rt_session_key(rt_sid)
        for retries in range(5):
            # 虽然不太可能但还是防范一下... 同一秒产生了多个连接请求,
            # 而生成的实时会话 ID 后缀的随机数也发生重复的情况
            if conn.hsetnx(rt_session_key, 'occupied', 1):
                is_sid_ok = True
                break

            # 果然重复了... 重新生成一个会话 ID
            # 这次就不用缓存的时间了
            rt_sid = sequences.time_ascending_suffixed()
            rt_session_key = get_rt_session_key(rt_sid)

        if not is_sid_ok:
            # 这一定不可能... 让客户端再做一次请求吧
            return None

        logged_in = user_obj is not None
        uid = user_obj['id'] if logged_in else None
        conn.hmset(rt_session_key, {
                'logged_in': 1 if logged_in else 0,
                'uid': uid or 0,
                'sid': sid,
                'login_token': login_token,
                'ctime': curtime,
                })

        if logged_in:
            # 当前用户已登陆, 记录到用户状态中, 并检查是否新上线
            user_sessions_key = get_user_sessions_key(uid)
            session_count = conn.rpush(user_sessions_key, rt_sid)
            if session_count == 1:
                # 确实是该用户的新上线会话, 发送 online 通知
                # TODO: 确定这里到底是写成全局事件还是用户事件好...
                # 在引入 app.session.tokens 之前是写的用户事件,
                # 但我觉得作为一个小社区的话, 还是多一点存在感比较好,
                # 也算是借鉴了 osu! 的 IRC 机制吧.
                # 性能问题这个阶段还是不用考虑的...
                pubsub.publish_global_event(
                        'user_online',
                        uid=uid,
                        # 同时送去用户的显示名称...
                        # 免得造成一大波又一大波的 account/xxx/stat/ 请求
                        display_name=user_obj['display_name'],
                        )
        else:
            # TODO: 处理未登陆用户
            pass

        return rt_sid

    def do_rt_logout(self, rt_sid):
        '''注销指定的实时会话 (正常窗口关闭/掉线等情况).'''

        conn = self.conn

        rt_session_key = get_rt_session_key(rt_sid)
        session_info = conn.hgetall(rt_session_key)
        if not session_info:
            # 这个会话已经不存在了... 什么都不做
            return

        # 删去会话
        conn.delete(rt_session_key)

        # 善后工作
        # 使用会话信息的时候要注意, 因为所有的值取回之后都变成了字符串...
        # 需要转换回原来的类型
        logged_in = int(session_info['logged_in']) != 0
        if logged_in:
            # 是已登陆用户的会话
            uid = session_info['uid']
            user_sessions_key = get_user_sessions_key(uid)

            # 从用户会话索引里删去当前会话, 检查还剩多少个会话
            # 剩下 0 个会话的话, 就发送 offline 通知
            with conn.pipeline() as pipe:
                pipe.lrem(user_sessions_key, 0, rt_sid)
                pipe.llen(user_sessions_key)
                results = pipe.execute()

            remaining_sessions = results[1]
            if remaining_sessions == 0:
                # 该用户已经没有活动的实时会话了, 发送通知
                user_obj = user.User.fetch(uid)
                pubsub.publish_global_event(
                        'user_offline',
                        uid=uid,
                        display_name=user_obj['display_name'],
                        )
        else:
            # 未登陆用户的会话
            # TODO: 处理未登陆用户
            pass


state_mgr = RTStateManager()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
