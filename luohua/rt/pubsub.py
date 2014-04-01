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
        'JSONPubSub',
        ]

try:
    import ujson as json
except ImportError:
    import json

from weiyu.db import db_hub

PUBSUB_STORAGE_ID = 'luohua.rt.pubsub'

DATA_MESSAGE_TYPES = frozenset({'message', 'pmessage', })

_PUBSUB_CLIENT_CACHE = []
_PUBLISH_CONNECTION = []


def _get_pubsub():
    if _PUBSUB_CLIENT_CACHE:
        return _PUBSUB_CLIENT_CACHE[0].pubsub()

    storage = db_hub.get_storage(PUBSUB_STORAGE_ID)
    client = storage.raw()
    _PUBSUB_CLIENT_CACHE.append(client)
    return client.pubsub()


def _get_publish_connection():
    if _PUBLISH_CONNECTION:
        return _PUBLISH_CONNECTION[0]

    pubsub = _get_pubsub()
    _PUBLISH_CONNECTION.append(pubsub)
    return pubsub


def publish_json(channel, data):
    return _get_publish_connection().publish(channel, json.dumps(data))


class JSONPubSub(object):
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
