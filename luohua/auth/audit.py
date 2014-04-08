#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 认证 / 审计记录
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
        'AUDIT_ENTRY_STRUCT_ID',
        'AuditEntry',
        ]

import six
import time

from weiyu.helpers.misc import smartbytes

from ..rt import pubsub
from ..utils import dblayer
from ..utils import sequences

AUDIT_ENTRY_STRUCT_ID = 'luohua.audit'

AUDIT_UID_IDX = b'audit_uid_bin'
AUDIT_MODULE_IDX = b'audit_module_bin'
AUDIT_ACTION_IDX = b'audit_act_bin'
AUDIT_GROUP_IDX = b'audit_group_bin'
AUDIT_TIMESTAMP_IDX = b'audit_ts_int'

AUDIT_MODULE_AUDIT = 'luohua.auth.audit'

AUDIT_TYPE_UPDATE = 'update'

_number_types = six.integer_types + (float, )


class AuditEntry(dblayer.RiakDocument):
    '''审计记录条目.'''

    struct_id = AUDIT_ENTRY_STRUCT_ID
    uses_2i = True

    def __init__(self, data=None, ts=None, rawobj=None):
        if ts is None:
            now = time.time()
            key = sequences.time_ascending_suffixed(int(now))
        else:
            key = ts

        super(AuditEntry, self).__init__(data, key, rawobj)

        if ts is None:
            self['ctime'] = now

    def _do_sync_2i(self, obj):
        obj.set_index(AUDIT_UID_IDX, smartbytes(self['uid']))
        obj.set_index(AUDIT_MODULE_IDX, smartbytes(self['module']))
        obj.set_index(AUDIT_ACTION_IDX, smartbytes(self['type']))
        obj.set_index(AUDIT_TIMESTAMP_IDX, int(self['ctime']))

        # 记录组
        group = self['group'] if 'group' in self else self['id']
        obj.set_index(AUDIT_GROUP_IDX, smartbytes(group))

        return obj

    def make_followup(self, uid, module, type, new_params):
        new_entry = self.__class__()
        new_entry['uid'] = uid
        new_entry['module'] = module
        new_entry['type'] = type
        new_entry['group'] = self['group']
        new_entry['params'] = new_params

        return new_entry

    def make_update_object(self, uid, new_params):
        return self.make_followup(
                uid,
                AUDIT_MODULE_AUDIT,
                AUDIT_TYPE_UPDATE,
                new_params,
                )


class BaseAuditedAction(object):
    '''审计事件类型.'''

    MODULE_NAME = None
    ACTION_TYPE = None

    def __init__(self, request, audit_entry=None, **kwargs):
        if audit_entry is None:
            self._check_params_spec(kwargs)

            user = request.user
            uid = user['id'] if user is not None else ''

            entry = AuditEntry()
            entry['remote_addr'] = request.remote_addr
            entry['uid'] = uid
            entry['module'] = self.MODULE_NAME
            entry['type'] = self.ACTION_TYPE
            entry['group'] = entry['id']
            entry['params'] = kwargs
        else:
            entry = audit_entry

        self.entry = entry

    def __new__(cls, **kwargs):
        if cls.MODULE_NAME is None:
            raise TypeError(
                    'cannot instantiate action object without module name'
                    )
        if cls.ACTION_TYPE is None:
            raise TypeError(
                    'cannot instantiate action object without action id'
                    )

        return super(BaseAuditedAction, cls).__new__(cls)

    @classmethod
    def _check_params_spec(cls, params):
        raise NotImplementedError

    def update(self, uid, new_params):
        self._check_params_spec(new_params)

        new_entry = self.entry.make_update_object(uid, new_params)
        new_entry.save()

        # 实时通知审计频道
        pubsub.publish_event('_auditlog', 'update', obj=new_entry)

    def save(self):
        self._check_params_spec(self.entry['params'])
        self.entry.save()

        # 实时通知审计频道
        pubsub.publish_event('_auditlog', 'save', obj=self.entry)


# 数据库序列化/反序列化
@AuditEntry.decoder(1)
def audit_entry_dec_v1(data):
    return {
            'remote_addr': data['r'],
            'uid': data['u'],
            'ctime': data['c'],
            'module': data['m'],
            'type': data['t'],
            'group': data['g'],
            'params': data['p'],
            }


@AuditEntry.encoder(1)
def audit_entry_enc_v1(ae):
    assert 'remote_addr' in ae
    assert isinstance(ae['remote_addr'], six.text_type)
    assert 'uid' in ae
    assert isinstance(ae['uid'], six.text_type)
    assert 'ctime' in ae
    assert isinstance(ae['ctime'], _number_types)
    assert 'module' in ae
    assert isinstance(ae['module'], six.text_type)
    assert '/' not in ae['module']
    assert 'type' in ae
    assert isinstance(ae['type'], six.text_type)
    assert '/' not in ae['type']
    assert 'params' in ae
    assert isinstance(ae['params'], dict)

    if 'group' in ae:
        group = ae['group']
        assert isinstance(group, six.text_type)
    else:
        group = ae['id']

    return {
            'r': ae['remote_addr'],
            'u': ae['uid'],
            'c': ae['ctime'],
            'm': ae['module'],
            't': ae['type'],
            'g': group,
            'p': ae['params'],
            }


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
