#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 认证 / 实名记录
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
        # 结构 ID
        'IDENT_FROZEN_STRUCT_ID',
        'IDENT_ENTRY_STRUCT_ID',
        # 实名记录类型
        'IDENT_TYPES',
        'IDENT_TYPES_STUDENT',
        'IDENT_TYPES_CURRENT_STUDENT',
        'IDENT_TYPE_UNDERGRAD',
        'IDENT_TYPE_GRADUATE',
        'IDENT_TYPE_ALUMNI',
        'IDENT_TYPE_STAFF',
        'IDENT_TYPE_OTHER',
        # 性别
        'GENDER_TYPES',
        'GENDER_NA',
        'GENDER_FEMALE',
        'GENDER_MALE',
        # 身份信息种类
        'ID_NUMBER_TYPES',
        'ID_NUMBER_TYPE_LAST6',
        # 编号/身份信息匹配返回值
        'IDENT_OK',
        'CHECK_IDENT_NOTFOUND',
        'CHECK_IDENT_INVALID_INPUT',
        'CHECK_IDENT_WRONG',
        # 新建可变身份信息记录返回值
        'NEW_IDENT_INVALID_TYPE',
        'NEW_IDENT_TYPE_NOT_IMPL',
        'NEW_IDENT_DUPLICATE',
        'NEW_IDENT_EMAIL',
        'NEW_IDENT_EMAIL_DUP',
        'NEW_IDENT_MOBILE',
        'NEW_IDENT_MOBILE_DUP',
        'NEW_IDENT_STUDENT_DORM_BLDG',
        'NEW_IDENT_STUDENT_DORM_ROOM',
        # 模块
        'validate_id_number',
        'FrozenIdent',
        'Ident',
        # 邮件模板
        'IdentVerifyMailMailTemplate',
        ]

import six

from weiyu.helpers.misc import smartbytes

from .. import univ
from ..utils import dblayer
from ..utils import randomness
from ..mail.template import MakoMailTemplate

from . import audit

IDENT_FROZEN_STRUCT_ID = 'luohua.ident.frozen'
IDENT_ENTRY_STRUCT_ID = 'luohua.ident.entry'

# 2i 索引
IDENT_ACTIVATION_KEY_INDEX = b'ident_ak_bin'
IDENT_EMAIL_INDEX = b'ident_e_bin'
IDENT_MOBILE_INDEX = b'ident_m_bin'

FIDENT_STUD_SCHOOL_INDEX = b'fident_ss_bin'
FIDENT_STUD_MAJOR_INDEX = b'fident_sm_bin'
FIDENT_STUD_CLASS_INDEX = b'fident_sc_bin'
FIDENT_STUD_YEAR_INDEX = b'fident_sy_bin'

# 实名记录类型
IDENT_TYPES = (
        IDENT_TYPE_UNDERGRAD,
        IDENT_TYPE_GRADUATE,
        IDENT_TYPE_ALUMNI,
        IDENT_TYPE_STAFF,
        IDENT_TYPE_OTHER,
        ) = six.moves.range(5)
IDENT_TYPES = frozenset(IDENT_TYPES)
IDENT_TYPES_STUDENT = frozenset({
        IDENT_TYPE_UNDERGRAD,
        IDENT_TYPE_GRADUATE,
        IDENT_TYPE_ALUMNI,
        })
IDENT_TYPES_CURRENT_STUDENT = frozenset({
        IDENT_TYPE_UNDERGRAD,
        IDENT_TYPE_GRADUATE,
        })

# 性别
GENDER_TYPES = GENDER_NA, GENDER_FEMALE, GENDER_MALE = six.moves.range(3)
GENDER_TYPES = frozenset(GENDER_TYPES)

# 身份信息种类
ID_NUMBER_TYPES = ID_NUMBER_TYPE_LAST6, = six.moves.range(1)
ID_NUMBER_TYPES = frozenset(ID_NUMBER_TYPES)

# 编号/身份信息匹配返回值, 新建可变身份信息记录返回值
(
        IDENT_OK,
        CHECK_IDENT_NOTFOUND,
        CHECK_IDENT_INVALID_INPUT,
        CHECK_IDENT_WRONG,
        NEW_IDENT_INVALID_TYPE,
        NEW_IDENT_TYPE_NOT_IMPL,
        NEW_IDENT_DUPLICATE,
        NEW_IDENT_EMAIL,
        NEW_IDENT_EMAIL_DUP,
        NEW_IDENT_MOBILE,
        NEW_IDENT_MOBILE_DUP,
        NEW_IDENT_STUDENT_INFO,
        NEW_IDENT_STUDENT_DORM_BLDG,
        NEW_IDENT_STUDENT_DORM_ROOM,
        ) = six.moves.range(14)

# 激活 key 相关常量
ACTIVATION_KEY_LENGTH = 32
ALREADY_ACTIVATED_KEY = '~'


def validate_id_number(id_number_type, id_number):
    if not isinstance(id_number, six.text_type):
        raise ValueError('ID number must be text type')

    if id_number_type == ID_NUMBER_TYPE_LAST6:
        if len(id_number) != 6:
            raise ValueError('ID_NUMBER_TYPE_LAST6: length must be 6')
        if not id_number[:5].isdigit():
            raise ValueError('ID_NUMBER_TYPE_LAST6: bad format')
        if id_number[5] not in '0123456789X':
            raise ValueError('ID_NUMBER_TYPE_LAST6: bad format')
    else:
        raise ValueError('unknown ID number type')


def _validate_info_pack_student(info):
    tmp = info.copy()

    # 字段存在性
    try:
        building = tmp.pop('student_dorm_building')
    except KeyError:
        return NEW_IDENT_STUDENT_DORM_BLDG

    try:
        room = tmp.pop('student_dorm_room')
    except KeyError:
        return NEW_IDENT_STUDENT_DORM_ROOM

    # 多余字段
    if tmp:
        return NEW_IDENT_STUDENT_INFO

    # 楼号存在性
    try:
        univ.dorm_info.query_building(building)
    except KeyError:
        return NEW_IDENT_STUDENT_DORM_BLDG

    # 房间号格式
    # TODO: 仅适用江南大学, 应该随各大学不同而有不同的判断
    if not isinstance(room, six.text_type):
        return NEW_IDENT_STUDENT_DORM_ROOM

    if len(room) != 3 or not room.isdigit():
        return NEW_IDENT_STUDENT_DORM_ROOM

    # TODO: 真正的寝室信息验证
    return IDENT_OK


class FrozenIdent(dblayer.RiakDocument):
    '''不可变实名信息.'''

    struct_id = IDENT_FROZEN_STRUCT_ID
    uses_2i = True

    def __init__(self, data=None, number=None, rawobj=None):
        super(FrozenIdent, self).__init__(data, number, rawobj)

    @classmethod
    def check_ident(cls, number, id_type, id_number):
        obj = cls.fetch(number)
        if obj is None:
            return CHECK_IDENT_NOTFOUND

        try:
            validate_id_number(id_type, id_number)
        except ValueError:
            return CHECK_IDENT_INVALID_INPUT

        obj_id_type, obj_id_number = obj['id_number_type'], obj['id_number']
        if id_type != obj_id_type or id_number != obj_id_number:
            return CHECK_IDENT_WRONG

        return IDENT_OK

    def _do_sync_2i(self, obj):
        obj.set_index(
                FIDENT_STUD_SCHOOL_INDEX,
                smartbytes(self['student_school']),
                )
        obj.set_index(
                FIDENT_STUD_MAJOR_INDEX,
                smartbytes(self['student_major']),
                )
        obj.set_index(
                FIDENT_STUD_CLASS_INDEX,
                smartbytes(self['student_class']),
                )
        obj.set_index(
                FIDENT_STUD_YEAR_INDEX,
                smartbytes(self['student_year']),
                )

        return obj


class Ident(dblayer.RiakDocument):
    '''实名信息.'''

    struct_id = IDENT_ENTRY_STRUCT_ID
    uses_2i = True

    def __init__(self, data=None, number=None, rawobj=None):
        super(Ident, self).__init__(data, number, rawobj)

        self._frozen_doc = None

    @property
    def frozen_info(self):
        '''与本条记录关联的不可变实名信息记录.'''

        if self._frozen_doc is not None:
            return self._frozen_doc

        if 'id' not in self:
            raise AttributeError('no ident id associated with this object')

        self._frozen_doc = FrozenIdent.fetch(self['id'])
        return self._frozen_doc

    def set_random_activation_key(self):
        '''设置一个随机的激活码, 用于新用户的邮箱认证.'''

        key = randomness.fixed_length_b64(ACTIVATION_KEY_LENGTH)
        self['activation_key'] = key

    def mark_activated(self):
        '''标记本条记录为已激活 (通过邮箱认证).'''

        self['activation_key'] = ALREADY_ACTIVATED_KEY

    def activate_mail_and_save(self, request):
        '''标记本条记录为已激活 (通过邮箱认证) 并保存.'''

        self.mark_activated()
        self.save()

        # 记录审计事件
        record = MailActivateAction(request, email=self['email'])
        record.save()

    @property
    def activated(self):
        '''本条记录是否已激活 (通过邮箱认证).'''

        # 没设置过这个字段的对象, 当然也算是没激活了
        return self.get('activation_key') == ALREADY_ACTIVATED_KEY

    @classmethod
    def from_activation_key(cls, key):
        '''试图根据激活码寻找一条实名记录.'''

        try:
            return cls._do_fetch_one_by_index(IDENT_ACTIVATION_KEY_INDEX, key)
        except dblayer.MultipleObjectsError:
            raise ValueError('Activation key collision: %s' % (key, ))

    @classmethod
    def from_email(cls, email):
        '''试图根据注册邮箱寻找一条实名记录.'''

        try:
            return cls._do_fetch_one_by_index(IDENT_EMAIL_INDEX, email)
        except dblayer.MultipleObjectsError:
            raise ValueError('Email collision: %s' % (email, ))

    @classmethod
    def from_mobile(cls, mobile):
        '''试图根据注册手机号寻找一条实名记录.'''

        try:
            return cls._do_fetch_one_by_index(IDENT_MOBILE_INDEX, mobile)
        except dblayer.MultipleObjectsError:
            raise ValueError('Mobile phone number collision: %s' % (mobile, ))

    def _do_sync_2i(self, obj):
        obj.set_index(IDENT_EMAIL_INDEX, self['email'])
        obj.set_index(IDENT_MOBILE_INDEX, self['mobile'])

        ak = self['activation_key']
        if ak != ALREADY_ACTIVATED_KEY:
            obj.set_index(IDENT_ACTIVATION_KEY_INDEX, ak)
        else:
            obj.remove_index(IDENT_ACTIVATION_KEY_INDEX)

        return obj

    @classmethod
    def new_ident(
            cls,
            typ,
            number,
            id_type,
            id_number,
            info,
            send_html_mail,
            request,
            ):
        # 打破循环依赖...
        from ..tasks import mail

        if typ not in IDENT_TYPES:
            return NEW_IDENT_INVALID_TYPE, None

        # TODO: 完善不同身份支持
        if typ not in IDENT_TYPES_CURRENT_STUDENT:
            return NEW_IDENT_TYPE_NOT_IMPL, None

        # 核对不可变身份信息
        chkresult = FrozenIdent.check_ident(number, id_type, id_number)
        if chkresult != IDENT_OK:
            return chkresult, None

        # 查重
        dup = cls.fetch(number)
        if dup is not None:
            return NEW_IDENT_DUPLICATE, None

        # 新建一条身份记录, 设置激活码
        obj = cls()
        obj['id'] = number
        obj['type'] = typ
        obj.set_random_activation_key()

        args = info.copy()
        # TODO: Email 合法性验证
        try:
            email = args.pop('email')
        except KeyError:
            return NEW_IDENT_EMAIL, None

        # Email 查重
        try:
            if cls.from_email(email) is not None:
                return NEW_IDENT_EMAIL_DUP, None
        except ValueError:
            # 已经有多于一个的这个 Email 了, 怎么回事...
            return NEW_IDENT_EMAIL_DUP, None

        # TODO: 手机号合法性验证
        try:
            mobile = args.pop('mobile')
        except KeyError:
            return NEW_IDENT_MOBILE, None

        # 手机号查重
        try:
            if cls.from_mobile(mobile) is not None:
                return NEW_IDENT_MOBILE_DUP, None
        except ValueError:
            # 同上
            return NEW_IDENT_MOBILE_DUP, None

        obj['email'] = email
        obj['mobile'] = mobile

        # 类型特异信息
        if typ in IDENT_TYPES_CURRENT_STUDENT:
            chkstud_ret = _validate_info_pack_student(args)
            if chkstud_ret != IDENT_OK:
                return chkstud_ret, None

            obj['student_dorm_building'] = args['student_dorm_building']
            obj['student_dorm_room'] = args['student_dorm_room']
        else:
            # TODO: 其他类型信息验证
            return NEW_IDENT_TYPE_NOT_IMPL, None

        obj.update(info)
        obj.save()

        # 记录审计事件
        record = IdentCreateAction(
                request,
                type=typ,
                email=email,
                mobile=mobile,
                )
        record.save()

        # 发送验证注册邮箱的邮件
        # NOTE: 考虑到数据库操作的延迟等不确定因素, 推迟任务执行 5 秒,
        # 同时设定任务时效性为 30 分钟 (为实现重试发送功能做准备)
        mail.send_ident_verify_mail_mail.apply_async(
                (
                    email,
                    number,
                    send_html_mail,
                ),
                countdown=5,
                expires=1800,
                )

        return IDENT_OK, obj


# 数据库序列化/反序列化
@Ident.decoder(1)
def ident_dec_v1(data):
    typ = data['t']
    result = {
            # 公共信息
            'type': typ,
            'email': data['e'],
            'mobile': data['m'],
            'activation_key': data['ak'],
            }

    if typ in IDENT_TYPES_STUDENT:
        result.update({
                # 学生专用字段
                'student_dorm_building': data['sdb'],
                'student_dorm_room': data['sdr'],
                })
    elif typ == IDENT_TYPE_STAFF:
        result.update({
                # 教职工字段
                'staff_site': data['ts'],
                })
    elif typ == IDENT_TYPE_OTHER:
        result.update({
                # 社会人员字段
                'other_full_id': data['oi'],
                'other_address': data['oa'],
                })
    else:
        raise ValueError('Wrong type field for ident %s' % (repr(data), ))

    return result


@Ident.encoder(1)
def ident_enc_v1(ident):
    # 公共信息
    assert 'type' in ident
    typ = ident['type']
    assert typ in IDENT_TYPES

    assert 'email' in ident
    assert isinstance(ident['email'], six.text_type)
    # TODO: assert ident['email'] 为合法 email 地址
    assert 'mobile' in ident
    assert isinstance(ident['mobile'], six.text_type)
    assert ident['mobile'].isdigit()

    assert 'activation_key' in ident
    ak = ident['activation_key']
    assert isinstance(ak, six.text_type)
    assert ak == ALREADY_ACTIVATED_KEY or len(ak) == ACTIVATION_KEY_LENGTH

    result = {
            # 公共信息
            't': ident['type'],
            'e': ident['email'],
            'm': ident['mobile'],
            'ak': ak,
            }

    if typ in IDENT_TYPES_STUDENT:
        # 学生专用字段
        assert 'student_dorm_building' in ident
        assert isinstance(ident['student_dorm_building'], six.integer_types)
        assert 'student_dorm_room' in ident
        assert isinstance(ident['student_dorm_room'], six.text_type)
        assert ident['student_dorm_room'].isdigit()

        result.update({
                # 学生专用字段
                'sdb': ident['student_dorm_building'],
                'sdr': ident['student_dorm_room'],
                })
        return result

    if typ == IDENT_TYPE_STAFF:
        # 教职工字段
        assert 'staff_site' in ident

        result.update({
                # 教职工字段
                'ts': ident['staff_site'],
                })
        return result

    if typ == IDENT_TYPE_OTHER:
        # 社会人员字段
        assert 'other_full_id' in ident
        # TODO: 完整身份证号校验
        assert isinstance(ident['other_full_id'], six.text_type)
        assert 'other_address' in ident
        assert isinstance(ident['other_address'], six.text_type)

        result.update({
                # 社会人员字段
                'oi': ident['other_full_id'],
                'oa': ident['other_address'],
                })
        return result

    # WTF?!
    assert False, 'should never happen'


@FrozenIdent.decoder(1)
def frozen_ident_dec_v1(data):
    typ = data['t']
    result = {
            # 公共信息
            'type': typ,
            'name': data['n'],
            'gender': data['g'],
            # 身份信息
            'id_number_type': data['it'],
            'id_number': data['in'],
            }

    if typ in IDENT_TYPES_CURRENT_STUDENT:
        # 学生信息
        result.update({
                'student_school': data['ss'],
                'student_major': data['sm'],
                'student_class': data['sc'],
                'student_year': data['sy'],
                })

    return result


@FrozenIdent.encoder(1)
def frozen_ident_enc_v1(ident):
    # 公共信息
    assert 'type' in ident
    typ = ident['type']
    assert typ in IDENT_TYPES

    assert 'name' in ident
    assert isinstance(ident['name'], six.text_type)

    assert 'gender' in ident
    assert ident['gender'] in GENDER_TYPES

    # 身份信息
    assert 'id_number_type' in ident
    assert 'id_number' in ident
    validate_id_number(ident['id_number_type'], ident['id_number'])

    result = {
            # 公共信息
            't': ident['type'],
            'n': ident['name'],
            'g': ident['gender'],
            # 身份信息
            'it': ident['id_number_type'],
            'in': ident['id_number'],
            }

    # 学生信息
    if typ in IDENT_TYPES_CURRENT_STUDENT:
        assert 'student_school' in ident
        assert 'student_major' in ident
        assert isinstance(ident['student_major'], six.text_type)
        assert 'student_class' in ident
        assert isinstance(ident['student_class'], six.integer_types)
        assert 'student_year' in ident
        assert isinstance(ident['student_year'], six.integer_types)

        result.update({
                'ss': ident['student_school'],
                'sm': ident['student_major'],
                'sc': ident['student_class'],
                'sy': ident['student_year'],
                })

    return result


# 审计事件
class BaseIdentAction(audit.BaseAuditedAction):
    MODULE_NAME = 'luohua.auth.ident'


class IdentCreateAction(BaseIdentAction):
    ACTION_TYPE = 'create'

    @classmethod
    def _check_params_spec(cls, params):
        assert 'type' in params
        assert 'email' in params
        assert 'mobile' in params


class MailActivateAction(BaseIdentAction):
    ACTION_TYPE = 'mail.activate'

    @classmethod
    def _check_params_spec(cls, params):
        assert 'email' in params


# 邮件模板
class IdentVerifyMailMailTemplate(MakoMailTemplate):
    text_template_path = 'mail/ident_verify_mail.txt.mako'
    html_template_path = 'mail/ident_verify_mail.html.mako'

    def get_subject(self):
        return '验证您的注册邮箱'


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
