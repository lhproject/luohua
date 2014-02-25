#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 数据结构 / 虚线索
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
from ..utils.sequences import time_descending
from .vfile import VFile

VTH_STRUCT_ID = 'luohua.vth'

VTH_VTP_INDEX = 'vtp_bin'
VTH_VTAG_INDEX = 'vtag_bin'
VTH_CTIME_INDEX = 'ctime_int'
VTH_MTIME_INDEX = 'mtime_int'
VTH_VTAG_CTIME_COMPOSITE_INDEX = 'vtagctime_bin'
VTH_VTAG_MTIME_COMPOSITE_INDEX = 'vtagmtime_bin'


class VThreadTree(object):
    '''虚线索树, 支持最多两层的回复 (楼中楼).

    这是落花存储线索类数据的核心. 之所以名字叫 "虚" 线索有以下几条原因:

    * 因为这个数据结构的外在表现形式不一定是一条讨论串,
    * 单名 "线索" 的英文名 ``Thread`` 和 "线程" 冲突,
    * 主要使用场景下线索的节点都是虚文件, 为了一致性而取了这个名字.

    '''

    def __init__(self, l):
        self._tree = l
        self._build_state()

    def __len__(self):
        '''本条虚线索的直接回复和楼中楼回复数.'''

        # 为了性能, 假定所有 node 对象在上面的字典里都不冲突
        # 这一点对实际使用情况的 VFile 对象做节点的情况是成立的
        # 于是节点总数就是节点字典的总长啦
        # self._len = 1 + sum(len(reply_l) for reply_l in self._tree[1:])
        return len(self._flatnodes)

    def num_direct_children(self):
        '''本条虚线索的直接回复数.'''

        return len(self._directreplies) - 1

    def num_pages(self, limit):
        '''本条虚线索总共需要占用的页数.'''

        pages, rem = divmod(len(self), limit)
        return pages if rem == 0 else pages + 1

    def __contains__(self, obj):
        '''判断某元素是否属于这条虚线索.'''

        return obj in self._nodes

    @property
    def tree(self):
        '''提供对虚线索树形结构的只读访问.

        对虚线索执行改动应该通过其他成员方法进行.

        '''

        return self._tree

    @property
    def root(self):
        '''提供对虚线索根节点的只读访问.'''

        return self._root

    def iter(self):
        '''按时间顺序遍历所有直接回复.'''

        yield self._root
        for node in self._nodes[self._root]:
            yield node

    def iter_time_order(self):
        '''按时间顺序遍历所有直接回复和楼中楼回复.

        用于实现传统阅读体验.

        '''

        # 直接对节点排序
        # 这一步的排序肯定需要避免重复进行, 否则时间复杂度会非常坏
        # TODO: 把结果缓存
        return sorted(self._flatnodes.iterkeys())

    def iter_paginated(self, limit, idx):
        '''按时间顺序对所有直接回复和楼中楼回复进行分页.

        用于支持移动端的分页浏览. 因为需要节约流量, 不方便实行客户端分页.

        '''

        # 需要借助上一步构造的时序遍历结果进行分页.
        # 如果上一步有缓存的话, 这一步的复杂度就是 O(n), 否则至少是 O(n^2)
        # TODO: 这一步的结果可能也需要缓存. 做 profile 确定必要性
        timeorder = list(self.iter_time_order())
        return iter(timeorder[limit * idx:limit * (idx + 1)])

    def append_to(self, in_reply_to, obj):
        '''添加回复.

        ``in_reply_to`` 为 ``None`` 则为直接回复, 否则为回复到该参数所指定的\
        楼中. 如果该参数所指元素不存在或不为直接回复, 则抛 :exc:`ValueError`.

        '''

        if in_reply_to is None:
            # 直接回复
            self._tree.append([obj, ])

            # 更新缓存
            self._directreplies.append(obj)
            self._reply_idx_map[obj] = len(self._tree) - 1  # 因为是最后一个
            self._nodes[self._root].append(obj)
            self._nodes[obj] = []
            self._flatnodes[obj] = self._root

            return

        # 寻找指定元素
        if in_reply_to not in self._nodes:
            # 能执行到这里也可能是因为压根不存在, 反正不是直接回复就对了
            raise ValueError("%s is not a direct reply" % repr(in_reply_to))

        # 更新树
        self._tree[self._reply_idx_map[in_reply_to]].append(obj)

        # 更新缓存
        self._nodes[in_reply_to].append(obj)
        self._flatnodes[obj] = in_reply_to

        return

    def _build_state(self):
        # 从嵌套列表构造树形结构
        # 先是根节点
        root = self._root = self._tree[0]
        self._nodes = {root: [reply_l[0] for reply_l in self._tree[1:]], }
        self._flatnodes = {root: None, }

        # 直接回复列表
        self._directreplies = [root] + self._nodes[root]

        # 直接回复对应原树形结构 index 的映射
        self._reply_idx_map = {}

        for reply_idx, reply_l in enumerate(self._tree[1:]):
            reply_root, subreplies = reply_l[0], reply_l[1:]

            # 更新 index 缓存
            # 注意那个 reply_idx 应该加上 1 才能对上原列表的序号
            self._reply_idx_map[reply_root] = reply_idx + 1

            # 更新树形结构缓存
            self._nodes[reply_root] = subreplies

            # 更新节点前驱缓存
            self._flatnodes[reply_root] = root
            self._flatnodes.update({sr: reply_root for sr in subreplies})


class VThread(RiakDocument):
    '''虚线索.

    本结构的存储后端应为 Riak.

    '''

    struct_id = VTH_STRUCT_ID
    uses_2i = True

    def __init__(self, data=None, vthid=None, rawobj=None):
        super(VThread, self).__init__(data, vthid, rawobj)

    @classmethod
    def _from_vtag(cls, idx, vtagid, time_start, time_end):
        # 复合索引 key
        key_start = '%s_%s' % (vtagid, time_descending(time_start), )
        key_end = '%s_%s' % (vtagid, time_descending(time_end), )
        return cls._do_fetch_range_by_index(
                idx,
                key_start,
                key_end,
                )

    @classmethod
    def from_vtag_ctime(cls, vtagid, time_start, time_end):
        return cls._from_vtag(
                VTH_VTAG_CTIME_COMPOSITE_INDEX,
                vtagid,
                time_start,
                time_end,
                )

    @classmethod
    def from_vtag_mtime(cls, vtagid, time_start, time_end):
        return cls._from_vtag(
                VTH_VTAG_MTIME_COMPOSITE_INDEX,
                vtagid,
                time_start,
                time_end,
                )

    def _do_sync_2i(self, obj):
        # 同步 2i 索引
        # 时间
        # 时间值在接下来同步复合检索索引的时候会用到, 先留下来
        ctime, mtime = self['ctime'], self['mtime']
        obj.set_index(VTH_CTIME_INDEX, ctime)
        obj.set_index(VTH_MTIME_INDEX, mtime)

        # 虚线索池
        obj.set_index(VTH_VTP_INDEX, self['vtpid'])

        # 虚标签, 虚标签-时间复合检索索引
        # 这里根本没必要计算差异, 因为实际存储的时候本来就是全部替换掉的
        # 直接扔掉旧索引创建新索引就行了
        new_vtags_set = set(self['vtags'])

        obj.remove_index(VTH_VTAG_INDEX)
        obj.remove_index(VTH_VTAG_CTIME_COMPOSITE_INDEX)
        obj.remove_index(VTH_VTAG_MTIME_COMPOSITE_INDEX)

        # 递减时间戳字符串
        descending_ctime = time_descending(ctime)
        descending_mtime = time_descending(mtime)

        for vtag in new_vtags_set:
            obj.add_index(VTH_VTAG_INDEX, vtag)

            ctime_idx_val = '%s_%s' % (vtag, descending_ctime, )
            mtime_idx_val = '%s_%s' % (vtag, descending_mtime, )
            obj.add_index(VTH_VTAG_CTIME_COMPOSITE_INDEX, ctime_idx_val)
            obj.add_index(VTH_VTAG_MTIME_COMPOSITE_INDEX, mtime_idx_val)

        return obj


@VThread.decoder(1)
def vth_dec_v1(data):
    return {
            'title': data['t'],
            'owner': data['o'],
            'ctime': data['c'],
            'mtime': data['m'],
            'tree': VThreadTree(data['r']),
            'vtags': data['g'],
            'vtpid': data['p'],
            'xattr': data['x'],
            }


@VThread.encoder(1)
def vth_enc_v1(vth):
    assert 'title' in vth
    assert isinstance(vth['title'], six.text_type)
    assert 'owner' in vth
    assert 'ctime' in vth
    assert isinstance(vth['ctime'], six.integer_types)
    assert 'mtime' in vth
    assert isinstance(vth['mtime'], six.integer_types)
    assert 'tree' in vth
    assert isinstance(vth['tree'], VThreadTree)
    assert 'vtags' in vth
    assert all(isinstance(tag, six.text_type) for tag in vth['vtags'])
    assert 'vtpid' in vth
    assert 'xattr' in vth
    assert isinstance(vth['xattr'], dict)

    return {
            't': vth['title'],
            'o': vth['owner'],
            'c': vth['ctime'],
            'm': vth['mtime'],
            'r': vth['tree'].tree,
            'g': vth['vtags'],
            'p': vth['vtpid'],
            'x': vth['xattr'],
            }


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
