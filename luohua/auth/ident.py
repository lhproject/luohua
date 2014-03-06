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

import six

from ..utils.dblayer import RiakDocument

IDENT_STRUCT_ID = 'luohua.ident'

IDENT_TYPES = (
        IDENT_TYPE_UNDERGRAD,
        IDENT_TYPE_GRADUATE,
        IDENT_TYPE_STAFF,
        IDENT_TYPE_OTHER,
        ) = six.moves.range(4)
IDENT_TYPES = frozenset(IDENT_TYPES)

GENDER_TYPES = GENDER_NA, GENDER_FEMALE, GENDER_MALE = six.moves.range(3)
GENDER_TYPES = frozenset(GENDER_TYPES)

ID_NUMBER_TYPES = ID_NUMBER_TYPE_LAST6, = six.moves.range(1)
ID_NUMBER_TYPES = frozenset(ID_NUMBER_TYPES)


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


class Ident(RiakDocument):
    struct_id = IDENT_STRUCT_ID

    def __init__(self, data=None, number=None, rawobj=None):
        super(Ident, self).__init__(data, number, rawobj)


# 数据库序列化/反序列化
@Ident.decoder(1)
def ident_dec_v1(data):
    return {
            # 公共信息
            'type': data['t'],
            'gender': data['g'],
            'email': data['e'],
            'mobile': data['m'],
            # 身份信息
            'id_number_type': data['it'],
            'id_number': data['in'],
            # 学生专用字段
            'student_school': data['ss'],
            'student_major': data['sm'],
            'student_class': data['sc'],
            'student_dorm_building': data['sdb'],
            'student_dorm_room': data['sdr'],
            # 教职工字段
            'staff_site': data['ts'],
            # 社会人员字段
            'other_address': data['oa'],
            }


@Ident.encoder(1)
def ident_enc_v1(ident):
    # 公共信息
    assert 'type' in ident
    assert ident['type'] in IDENT_TYPES
    assert 'gender' in ident
    assert ident['gender'] in GENDER_TYPES
    assert 'email' in ident
    assert isinstance(ident['email'], six.text_type)
    # TODO: assert ident['email'] 为合法 email 地址
    assert 'mobile' in ident
    assert isinstance(ident['mobile'], six.text_type)
    assert ident['mobile'].isdigit()
    # 身份信息
    assert 'id_number_type' in ident
    assert 'id_number' in ident
    validate_id_number(ident['id_number_type'], ident['id_number'])
    # 学生专用字段
    assert 'student_school' in ident
    assert 'student_major' in ident
    assert isinstance(ident['student_major'], six.text_type)
    assert 'student_class' in ident
    assert isinstance(ident['student_class'], six.integer_types)
    assert 'student_dorm_building' in ident
    assert isinstance(ident['student_dorm_building'], six.integer_types)
    assert 'student_dorm_room' in ident
    assert isinstance(ident['student_dorm_room'], six.text_type)
    assert ident['student_dorm_room'].isdigit()
    # 教职工字段
    assert 'staff_site' in ident
    # 社会人员字段
    assert 'other_address' in ident
    assert isinstance(ident['other_address'], six.text_type)

    return {
            # 公共信息
            'n': ident['number'],
            't': ident['type'],
            'g': ident['gender'],
            'e': ident['email'],
            'm': ident['mobile'],
            # 身份信息
            'it': ident['id_number_type'],
            'in': ident['id_number'],
            # 学生专用字段
            'ss': ident['student_school'],
            'sm': ident['student_major'],
            'sc': ident['student_class'],
            'sdb': ident['student_dorm_building'],
            'sdr': ident['student_dorm_room'],
            # 教职工字段
            'ts': ident['staff_site'],
            # 社会人员字段
            'oa': ident['other_address'],
            }


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
