#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 落花 / 数据结构 / 虚线索
#
# Copyright (C) 2013 JNRain
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


class VThread(object):
    def __init__(self, l):
        self._tree = l
        self._build_state()

    def __len__(self):
        '''本条虚线索的直接回复和楼中楼回复数。'''

        return self._len

    def num_direct_children(self):
        '''本条虚线索的直接回复数。'''

        return len(self._directreplies) - 1

    def num_pages(self, limit):
        '''本条虚线索总共需要占用的页数。'''

        pages, rem = divmod(len(self), limit)
        return pages if rem == 0 else pages + 1

    def __contains__(self, obj):
        '''判断某元素是否属于这条虚线索。'''

        return obj in self._nodes

    @property
    def tree(self):
        '''提供对虚线索树形结构的只读访问。

        对虚线索执行改动应该通过其他成员方法进行。

        '''

        return self._tree

    @property
    def root(self):
        '''提供对虚线索根节点的只读访问。'''

        return self._root

    def iter(self):
        '''按时间顺序遍历所有直接回复。'''

        yield self._root
        for node in self._nodes[self._root]:
            yield node

    def iter_time_order(self):
        '''按时间顺序遍历所有直接回复和楼中楼回复。

        用于实现传统阅读体验。

        '''

        # 直接对节点排序
        # 这一步的排序肯定需要避免重复进行，否则时间复杂度会非常坏
        # TODO: 把结果缓存
        return sorted(self._flatnodes.iterkeys())

    def iter_paginated(self, limit, idx):
        '''按时间顺序对所有直接回复和楼中楼回复进行分页。

        用于支持移动端的分页浏览。因为需要节约流量，不方便实行客户端分页。

        '''

        # 需要借助上一步构造的时序遍历结果进行分页。
        # 如果上一步有缓存的话，这一步的复杂度就是 O(n)，否则至少是 O(n^2)
        # TODO: 这一步的结果可能也需要缓存。做 profile 确定必要性
        timeorder = list(self.iter_time_order())
        return iter(timeorder[limit * idx:limit * (idx + 1)])

    def _build_state(self):
        # 从嵌套列表构造树形结构
        # 先是根节点
        root = self._root = self._tree[0]
        self._nodes = {root: [reply_l[0] for reply_l in self._tree[1:]], }
        self._flatnodes = {root: None, }

        # 直接回复列表
        self._directreplies = [root] + self._nodes[root]

        for reply_l in self._tree[1:]:
            reply_root, subreplies = reply_l[0], reply_l[1:]

            # 更新树形结构缓存
            self._nodes[reply_root] = subreplies

            # 更新节点前驱缓存
            self._flatnodes[reply_root] = root
            self._flatnodes.update({sr: reply_root for sr in subreplies})

        # 计算并缓存长度数据
        # 为了性能，假定所有 node 对象在上面的字典里都不冲突
        # 这一点对实际使用情况的 VFile 对象做节点的情况是成立的
        # 于是节点总数就是节点字典的总长啦
        # self._len = 1 + sum(len(reply_l) for reply_l in self._tree[1:])
        self._len = len(self._flatnodes)


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
