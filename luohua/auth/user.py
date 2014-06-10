#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 认证 / 用户
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

import six
import time

from weiyu.helpers.misc import smartbytes
from ..utils import dblayer
from ..utils import sequences
from ..rt import pubsub

from . import audit
from . import passwd
from . import ident
from . import role

USER_STRUCT_ID = 'luohua.user'

USER_ALIAS_IDX = b'user_alias_bin'
USER_IDENT_IDX = b'user_ident_bin'
USER_DISPLAY_NAME_IDX = b'user_nd_bin'
USER_ROLES_IDX = b'user_roles_bin'

# 注册用户返回值
NEW_USER_OK = 0
(
        NEW_USER_DUP,
        NEW_USER_PASSWORD_TOO_WEAK,
        NEW_USER_DISPLAY_NAME,
        NEW_USER_DISPLAY_NAME_LENGTH,
        NEW_USER_DISPLAY_NAME_DUP,
        ) = range(101, 106)

# 常量
DISPLAY_NAME_MAX_LENGTH = 16


class User(dblayer.RiakDocument):
    struct_id = USER_STRUCT_ID
    uses_2i = True

    def __init__(self, data=None, uid=None, rawobj=None):
        super(User, self).__init__(data, uid, rawobj)

        self._ident_cache = []

    def chkpasswd(self, psw):
        '''进行密码验证。'''

        psw_obj = self['password']
        return psw_obj.check(psw)

    @classmethod
    def find_by_ident(cls, ident):
        '''寻找实名身份符合 ident 的用户.'''

        # 按实名身份索引检索
        by_ident = list(cls._do_fetch_by_index(USER_IDENT_IDX, ident))
        if by_ident:
            # 当前情况下, 多于一个就报错
            if len(by_ident) > 1:
                raise ValueError('>1 user with the same ident: %s' % (ident, ))

            return by_ident[0]

        return None

    @classmethod
    def find_by_alias(cls, alias):
        '''寻找 KBS 帐户名符合 alias 的用户.'''

        # 按 KBS 帐户名索引检索
        by_alias = list(cls._do_fetch_by_index(USER_ALIAS_IDX, alias))
        if by_alias:
            # 同上
            if len(by_alias) > 1:
                raise ValueError('>1 user with the same alias: %s' % (alias, ))

            return by_alias[0]

        return None

    @classmethod
    def find_by_display_name(cls, name):
        '''寻找显示名称符合 name 的用户.'''

        try:
            return cls._do_fetch_one_by_index(USER_DISPLAY_NAME_IDX, name)
        except dblayer.MultipleObjectsError:
            raise ValueError('user display name collision: %s' % (name, ))

    @classmethod
    def find_by_guess(cls, name):
        '''寻找登陆身份符合 name 的用户.

        将按照以下顺序检测 ``name``:

        1. 学号/工号
        2. 显示名称
        3. KBS 帐户名

        '''

        result_by_ident = cls.find_by_ident(name)
        if result_by_ident is not None:
            return result_by_ident

        result_by_display_name = cls.find_by_display_name(name)
        if result_by_display_name is not None:
            return result_by_display_name

        result_by_alias = cls.find_by_alias(name)
        if result_by_alias is not None:
            return result_by_alias

        return None

    @property
    def caps(self):
        return role.Role.allcaps(self['roles'])

    @property
    def ident(self):
        try:
            return self._ident_cache[0]
        except IndexError:
            pass

        ident_obj = ident.Ident.fetch(self['ident'])
        self._ident_cache.append(ident_obj)
        return ident_obj

    def _do_sync_2i(self, obj):
        obj.set_index(USER_IDENT_IDX, smartbytes(self['ident']))
        obj.set_index(USER_DISPLAY_NAME_IDX, smartbytes(self['display_name']))

        if 'alias' in self:
            obj.set_index(USER_ALIAS_IDX, smartbytes(self['alias']))

        # 角色
        obj.remove_index(USER_ROLES_IDX)
        for role in self['roles']:
            obj.add_index(USER_ROLES_IDX, smartbytes(role))

        return obj

    @classmethod
    def new_user(
            cls,
            password,
            ident_type,
            ident_number,
            ident_id_type,
            ident_id_number,
            ident_info,
            display_name,
            send_html_mail,
            request,
            xattr=None,
            ):
        xattr = xattr if xattr is not None else {}

        # 查重
        if cls.find_by_ident(ident_number) is not None:
            return NEW_USER_DUP, None

        # 检查显示名称
        if not isinstance(display_name, six.text_type):
            return NEW_USER_DISPLAY_NAME, None
        if len(display_name) > DISPLAY_NAME_MAX_LENGTH:
            return NEW_USER_DISPLAY_NAME_LENGTH, None

        # 显示名称查重
        if cls.find_by_display_name(display_name) is not None:
            return NEW_USER_DISPLAY_NAME_DUP, None

        # 检查显示名称与 KBS 帐户的可能冲突
        if cls.find_by_alias(display_name) is not None:
            return NEW_USER_DISPLAY_NAME_DUP, None

        # 验证 ident
        ident_result, ident_obj = ident.Ident.new_ident(
                ident_type,
                ident_number,
                ident_id_type,
                ident_id_number,
                ident_info,
                send_html_mail,
                request,
                )
        if ident_result != ident.IDENT_OK:
            return ident_result, None

        user = cls()
        user['id'] = sequences.time_ascending_suffixed()

        # 新用户不会有 KBS 用户名
        # TODO: 检查弱密码
        user['password'] = passwd.new_password(password)
        user['alias'] = None

        # 其他基本设置
        user['display_name'] = display_name
        user['display_name_mtime'] = int(time.time())
        user['ident'] = ident_obj['id']
        user['roles'] = {'initial', }
        user['xattr'] = xattr

        # 记录初始个性化设置
        # HTML 邮件喜好
        user.prefs['mail.html'] = send_html_mail

        user.save()

        # 记录审计事件
        record = UserCreateAction(
                request,
                display_name=display_name,
                ident=ident_obj['id'],
                )
        record.save()

        # 发送一条实时信息
        pubsub.publish_global_event('new_user', display_name=display_name)

        return NEW_USER_OK, user

    @property
    def prefs(self):
        '''用户个性化设置存储.'''

        xattr = self['xattr']

        try:
            return xattr['prefs']
        except KeyError:
            pass

        xattr['prefs'] = {}
        return xattr['prefs']


# 数据库序列化/反序列化
@User.decoder(1)
def user_dec_v1(data):
    # KBS 兼容性...
    alias = data.get('a', None)

    # NOTE: 密码的 uid 字段只有 KBS 的 hash 算法用到, 而只有 KBS 导入的用户
    # 才有 KBS 格式的 hash, 所以这里对没有设置别名的用户传入空字符串是完全
    # 没有问题的
    return {
            'password': passwd.Password(alias or '', data['p']),
            'alias': alias,
            'display_name': data['nd'],
            'display_name_mtime': data['ndm'],
            'ident': data['i'],
            'roles': set(data['r']),
            'xattr': data['x'],
            }


@User.encoder(1)
def user_enc_v1(user):
    assert 'password' in user
    assert isinstance(user['password'], passwd.Password)
    assert 'alias' in user
    if user['alias'] is not None:
        assert isinstance(user['alias'], six.text_type)

    assert 'display_name' in user
    display_name = user['display_name']
    assert isinstance(display_name, six.text_type)
    assert len(display_name) <= DISPLAY_NAME_MAX_LENGTH

    assert 'display_name_mtime' in user
    assert isinstance(user['display_name_mtime'], six.integer_types)

    assert 'ident' in user
    assert isinstance(user['ident'], six.text_type)
    assert 'roles' in user
    assert isinstance(user['roles'], set)
    assert 'xattr' in user
    assert isinstance(user['xattr'], dict)

    return {
            'p': user['password'].psw_hash,
            'a': user['alias'],
            'nd': display_name,
            'ndm': user['display_name_mtime'],
            'i': user['ident'],
            'r': list(user['roles']),
            'x': user['xattr'],
            }


# 审计事件
class BaseUserAction(audit.BaseAuditedAction):
    MODULE_NAME = 'luohua.auth.user'


class UserCreateAction(BaseUserAction):
    ACTION_TYPE = 'create'

    @classmethod
    def _check_params_spec(cls, params):
        assert 'display_name' in params
        assert 'ident' in params


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
