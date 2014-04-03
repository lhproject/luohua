#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 实时信道 / PubSub 机制
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
        'publish_json',
        'publish_event',
        'publish_global_event',
        'JSONPubSub',
        ]

try:
    import ujson as json
except ImportError:
    import json

from weiyu.db import db_hub

PUBSUB_STORAGE_ID = 'luohua.rt.pubsub'
PUBSUB_CHANNEL_PREFIX = '/lh/'

DATA_MESSAGE_TYPES = frozenset({'message', 'pmessage', })

_PUBSUB_CLIENT_CACHE = []


def _get_pubsub_client():
    if _PUBSUB_CLIENT_CACHE:
        return _PUBSUB_CLIENT_CACHE[0]

    storage = db_hub.get_storage(PUBSUB_STORAGE_ID)
    client = storage.raw()
    _PUBSUB_CLIENT_CACHE.append(client)
    return client


def _get_pubsub():
    return _get_pubsub_client().pubsub()


def publish_json(channel, data):
    '''向指定频道发送任意 JSON 数据.

    .. note::

        如果只是想发送一条实时事件通知, 最好使用 :func:`publish_event` 或者
        :func:`publish_global_event`, 用法更简单且更易维护.

    :param channel: PubSub 频道名; 在传入 Redis 之前会被冠上 ``/lh/`` 的前缀.
    :type channel: :data:`six.text_type`
    :param data: 要发送的数据.
    :return: 消息总共抵达的订阅端总数.
    :rtype: :data:`six.integer_types`

    '''

    channel_name = PUBSUB_CHANNEL_PREFIX + channel
    return _get_pubsub_client().publish(channel_name, json.dumps(data))


def publish_event(channel, typ, **kwargs):
    '''发送一条事件消息到一个频道. 传入的命名参数会成为消息的一部分.

    .. note::

        如果想在全局 (全站) 范围发送消息, 请使用 :func:`publish_global_event`,
        不要重复书写全局频道名.

    :param channel: PubSub 频道名.
    :type channel: :data:`six.text_type`
    :param typ: 事件类型, 如 ``'mentioned'`` 或 ``'friend_online'`` 等.
    :type typ: :data:`six.text_type`
    :param kwargs: 事件参数.
    :return: 消息总共抵达的订阅端总数.
    :rtype: :data:`six.integer_types`

    '''

    kwargs['type'] = typ
    return publish_json('evt/' + channel, kwargs)


def publish_global_event(typ, **kwargs):
    '''发送一条事件消息到全局事件频道.

    :param typ: 事件类型, 如 ``'new_user'`` 或 ``'online_status'`` 等.
    :type typ: :data:`six.text_type`
    :param kwargs: 事件参数.
    :return: 消息总共抵达的订阅端总数.
    :rtype: :data:`six.integer_types`

    '''

    return publish_event('GLOBAL', typ, **kwargs)


class JSONPubSub(object):
    '''使用 JSON 作为传输格式的 Redis PubSub 包装.'''

    def __init__(self):
        self.pubsub = _get_pubsub()

    def subscribe(self, channels):
        return self.pubsub.subscribe(channels)

    def psubscribe(self, patterns):
        return self.pubsub.psubscribe(patterns)

    def unsubscribe(self, channels=[]):
        return self.pubsub.unsubscribe(channels)

    def punsubscribe(self, patterns=[]):
        return self.pubsub.punsubscribe(patterns)

    def listen(self):
        for msg in self.pubsub.listen():
            msg_type = msg['type']
            if msg_type in DATA_MESSAGE_TYPES:
                data = json.loads(msg['data'])

                yield {
                        'type': msg_type,
                        'pattern': msg['pattern'],
                        'channel': msg['channel'],
                        'data': data,
                        }
            else:
                yield msg


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
