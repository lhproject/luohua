#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 管理工具 / 数据导入 / 不可变实名信息
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

from ...auth import ident


def import_frozen_idents(data):
    '''向数据库导入不可变实名信息.

    接受一个包含欲导入记录的列表, 记录格式形如::

        {
            'id': '1030567890',  # 学号
            'type': 0,  # 记录性质, 0 为本科生, 1 为研究生, 2 为教职工
            'name': '王尼玛',  # 姓名
            'male': True,  # 性别, 男性为真
            'id_number_type': 0,  # 身份证号类型, 0 为后六位
            'id_number': '12345X',  # 身份证号

            # 以下为学生专用字段
            'school': '数字媒体学院',  # 学院名称
            'major': '0305',  # 专业代码
            'klass': 1,  # 班级序号, 如为研究生则忽略此字段
            'year': 2013,  # 入学年份

            # 以下为教职工专用字段
            'site': '校行政',  # 工作地点
        }

    注意所有字符串都应该是文本类型 (:data:`six.text_type`), 在 Python 2.x
    下应为 ``unicode``, Python 3.x 下应为 ``str``, 否则会导致乱码或抛出异常.

    :param data: 欲导入的记录列表
    :type data: list
    :return: 导入失败的记录列表, 每条记录形如 ``(原始记录, 抛出的异常, )``
    :rtype: list

    '''

    failures = []

    with ident.FrozenIdent.storage as conn:
        for record in data:
            try:
                obj = ident.FrozenIdent()

                # 公共信息
                obj['id'] = record['id']
                typ = obj['type'] = record['type']
                obj['name'] = record['name']
                obj['gender'] = (
                        ident.GENDER_MALE
                        if record['male']
                        else ident.GENDER_FEMALE
                        )
                obj['id_number_type'] = record['id_number_type']
                obj['id_number'] = record['id_number']

                # 学生信息
                if typ == ident.IDENT_TYPE_UNDERGRAD:
                    obj['student_school'] = record['school']
                    obj['student_major'] = record['major']
                    obj['student_class'] = record['klass']
                    obj['student_year'] = record['year']
                elif typ == ident.IDENT_TYPE_GRADUATE:
                    obj['student_school'] = record['school']
                    obj['student_major'] = record['major']
                    obj['student_year'] = record['year']
                elif typ == ident.IDENT_TYPE_STAFF:
                    obj['staff_site'] = record['site']
                else:
                    raise NotImplementedError(
                            'TODO: ident type %s' % (
                                repr(typ),
                                ))

                obj.save_to_conn(conn)
            except Exception as e:
                failures.append((record, e, ))

    return failures


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
