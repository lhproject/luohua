#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 任务队列 / Celery 接口
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

from __future__ import absolute_import, unicode_literals

__all__ = [
        'app',
        'jsontask',
        ]

import os

from celery import Celery

from weiyu.init import boot
from weiyu.registry.provider import request as regrequest

# 走到项目根目录, 初始化微雨框架
# 因为微雨框架已经有了针对多次初始化的保护措施, 所以在应用服务器的组件里导入
# Celery 任务也不会出问题.
project_root = os.path.join(os.path.dirname(__file__),  '../..')
os.chdir(project_root)
boot()


class ConfigPlaceholder(object):
    pass


def _read_config():
    task_reg, config_obj = regrequest('luohua.celery'), ConfigPlaceholder()
    for k, v in task_reg.items():
        setattr(config_obj, k, v)

    return config_obj


app = Celery('luohua')
app.config_from_object(_read_config())


def jsontask(fn):
    '''定义任务用的修饰符, ``@app.task(serializer='json')`` 的省略.'''

    return app.task(serializer='json')(fn)


if __name__ == '__main__':
    app.start()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
