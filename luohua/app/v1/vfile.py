#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 应用 / API v1 / 虚文件
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

try:
    import ujson as json
except ImportError:
    import json

import six
import time

from weiyu.helpers.misc import smartstr
from weiyu.shortcuts import http, jsonview
from weiyu.utils.decorators import only_methods

from ..session.decorators import require_cap
from ...utils.viewhelpers import jsonreply, parse_form
from ...utils.sequences import time_ascending_suffixed
from ...datastructures.vtag import VTag
from ...datastructures.vthread import VThread, VThreadTree
from ...datastructures.vfile import VFile


def _new_vfid(timestamp):
    for trial in xrange(5):
        temp_vfid = time_ascending_suffixed(timestamp)
        if VFile.fetch(temp_vfid) is None:
            # 不重复, 可用
            return temp_vfid
    raise RuntimeError('UNLIKELY: failed to generate sequential vfid')


def _new_vthid(timestamp):
    for trial in xrange(5):
        temp_vthid = time_ascending_suffixed(timestamp)
        if VThread.fetch(temp_vthid) is None:
            # 不重复, 可用
            return temp_vthid
    raise RuntimeError('UNLIKELY: failed to generate sequential vthid')


@http
@jsonview
def vfile_read_v1_view(request, vfid):
    '''v1 虚文件读取接口.

    :Allow: GET
    :URL 格式: :wyurl:`api:vfile-read-v1`
    :GET 参数:
        ====== ========= ==================================================
         字段   类型      说明
        ====== ========= ==================================================
         vfid   unicode   虚文件 ID
        ====== ========= ==================================================

    :POST 参数: 无
    :返回:
        :r:
            === ===========================================================
             0   查询成功
             2   所请求的虚文件不存在
            === ===========================================================

        :s:
            所请求虚文件的内容. 如果查询不成功, 此属性不存在.

            ====== ========= ==============================================
             字段   类型     说明
            ====== ========= ==============================================
             t      unicode   虚文件标题
             o      unicode   所有者 ID
             c      int       创建时间 Unix 时间戳
             n      unicode   虚文件内容
             f      unicode   虚文件内容格式, 如 ``'txt'`` 或 ``'ubb'``
             x      dict      虚文件上附着的扩展属性
            ====== ========= ==============================================

    :副作用: 无

    '''

    vf = VFile.fetch(vfid)
    if vf is None:
        return jsonreply(r=2)

    # If-Modified-Since
    client_cache_ts = request.conditional.get('If-Modified-Since', None)
    if client_cache_ts is not None:
        if vf['ctime'] <= client_cache_ts:
            return 304, {}, {'last_modified': vf['ctime'], }

    stat_obj = {
            't': vf['title'],
            'o': vf['owner'],
            'c': vf['ctime'],
            'n': vf['content'],
            'f': vf['format'],
            'x': vf['xattr'],
            }

    return (
            200,
            {
                'r': 0,
                's': stat_obj,
                },
            {
                'last_modified': vf['ctime'],
                },
            )


@http
@jsonview
@require_cap('vf-creat')
def vfile_creat_v1_view(request):
    '''v1 虚文件创建接口.

    .. note::

        API v1 只能创建 Markdown 格式的虚文件,
        这个限制将在之后的 API 版本中解除.

    :Allow: POST
    :URL 格式: :wyurl:`api:vfile-creat-v1`
    :GET 参数: 无
    :POST 参数:
        ========= ========= ===============================================
         字段      类型     说明
        ========= ========= ===============================================
         vthid     unicode   **可选** 新建虚文件从属于哪个虚线索,
                             省略则自动新建对应的虚线索
         vtpid     unicode   新建虚文件所属虚线索池 ID,
                             新建虚线索时\ **必须**\ 传入, 否则\ **不能**\
                             传入
         vtags     list      新建虚文件所属的虚标签列表, 长度至少为 1.
                             新建虚线索时\ **必须**\ 传入, 否则\ **不能**\
                             传入
         inreply2  unicode   **可选** 新建虚文件属于哪个虚文件的直接回复.
                             只能支持一层间接回复; 省略则回复楼主.
                             新建虚线索时此参数\ **不能**\ 传入
         title     unicode   **可选** 虚文件标题,
                             新建虚线索时\ **必须**\ 传入
         content   unicode   **必须** 虚文件内容
        ========= ========= ===============================================

    :返回:
        :r:
            ===== =========================================================
             0     创建成功
             22    传入参数格式不正确
             101   有一些所请求的虚标签不存在
             102   指定的虚线索不存在
             103   在指定虚线索中要回复的虚文件不存在, 或已经为楼中楼回复
            ===== =========================================================

        :f: 新建虚文件的 ID. 如果创建不成功, 此属性不存在.
        :t:
            新建虚线索的 ID. 如果不是顺带新建虚线索的请求或创建不成功,
            此属性不存在.

    :副作用:

        如果调用成功, 会创建一个虚文件, 或者根据参数, 可能顺带新建一个虚线索.
        调用不成功则无副作用.

    '''

    try:
        vtpid, vtags, vthid, inreply2, title, content = parse_form(
                request,
                'vtpid',
                'vtags',
                'vthid',
                'inreply2',
                'title',
                'content',
                vtpid=None,
                vtags=None,
                vthid=None,
                inreply2=None,
                title=None,
                )
    except KeyError:
        return jsonreply(r=22)

    # 是否顺便新建 VThread
    is_new_vth = vthid is None

    # 预先把 UTF-8 编码解开
    title_str = smartstr(title) if title is not None else None
    content_str = smartstr(content)

    if is_new_vth:
        # 传入请求是因为需要又一次验证权限
        return _do_creat_vf_with_vth(
                request,
                vtpid,
                vtags,
                inreply2,
                title_str,
                content_str,
                )

    return _do_creat_vf_reply(
            request,
            vtpid,
            vtags,
            vthid,
            inreply2,
            title_str,
            content_str,
            )


@require_cap('vth-creat')
def _do_creat_vf_with_vth(
            request,
            vtpid,
            vtags,
            inreply2,
            title,
            content,
            ):
    '''新建一组虚线索和虚文件并保存.'''

    # 如果新建 VThread, title 必须, vtpid 必须, vtags 必须,
    # inreply2 不能传入 (无意义)
    if title is None or vtpid is None or vtags is None:
        return jsonreply(r=22)

    if inreply2 is not None:
        return jsonreply(r=22)

    # 验证 VTag ID 列表
    if not isinstance(vtags, list):
        return jsonreply(r=22)

    if not all(isinstance(vtagid, six.text_type) for vtagid in vtags):
        return jsonreply(r=22)

    # 验证 VTag 存在性
    for vtagid in vtags:
        vtag = VTag.fetch(vtagid)
        if vtag is None or vtag['vtpid'] != vtpid:
            return jsonreply(r=101)

    # 记录时间一次, 之后都用这个
    now = int(time.time())

    # 当前用户的信息快照
    assert request.user is not None
    uid, user_snapshot = smartstr(request.user['id']), request.user.encode()

    # 新建 VFile
    new_vf = VFile()
    new_vf['id'] = _new_vfid(now)

    new_vf['owner'] = uid
    new_vf['owner_snapshot'] = user_snapshot
    new_vf['ctime'] = now
    new_vf['title'] = title
    new_vf['content'] = content

    # API v1 里把内容格式写死算了
    new_vf['format'] = 'md'

    new_vf['xattr'] = {}
    new_vf.save()

    # 新建 VThread
    new_vth = VThread()
    new_vth['id'] = _new_vthid(now)
    new_vth['title'] = title
    new_vth['owner'] = uid
    new_vth['owner_snapshot'] = user_snapshot
    new_vth['ctime'] = now
    new_vth['mtime'] = now
    new_vth['tree'] = VThreadTree([new_vf['id'], ])
    new_vth['vtags'] = vtags
    new_vth['vtpid'] = vtpid
    new_vth['xattr'] = {}
    new_vth.save()

    return jsonreply(r=0, f=new_vf['id'], t=new_vth['id'], )


def _do_creat_vf_reply(
        request,
        vtpid,
        vtags,
        vthid,
        inreply2,
        title,
        content,
        ):
    '''新建一个虚文件回复并保存.'''

    # 如果新建回复, vtpid, vtags 不能传入
    if vtpid is not None or vtags is not None:
        return jsonreply(r=22)

    vth = VThread.fetch(vthid)
    if vth is None:
        return jsonreply(r=102)

    # 是否为新建楼中楼回复?
    if inreply2 is not None:
        # 该条虚线索里有没有这个 VFile?
        if inreply2 not in vth['tree']:
            return jsonreply(r=103)

    now = int(time.time())

    # 当前用户的信息快照
    assert request.user is not None
    uid, user_snapshot = smartstr(request.user['id']), request.user.encode()

    # 创建虚文件
    new_vf = VFile()
    new_vf['id'] = _new_vfid(now)
    new_vf['owner'] = uid
    new_vf['owner_snapshot'] = user_snapshot
    new_vf['ctime'] = int(time.time())
    new_vf['title'] = title if title is not None else ''
    new_vf['content'] = content

    # 见上, 写死内容格式
    new_vf['format'] = 'md'

    new_vf['xattr'] = {}
    new_vf.save()

    # 更新虚线索
    # inreply2 为 None 则为直接回复, 这个参数的语义和 VThreadTree 里的实现
    # 正好是一致的, 就直接传了
    vth['mtime'] = now
    vth['tree'].append_to(inreply2, new_vf['id'])
    vth.save()

    return jsonreply(r=0, f=new_vf['id'], )


@http
@jsonview
def vfile_fcntl_v1_view(request, vfid):
    raise NotImplementedError


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
