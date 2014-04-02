数据库抽象层
~~~~~~~~~~~~

.. autoclass:: luohua.utils.dblayer.RiakDocument
    :members:
    :private-members:

    .. attribute:: uses_2i

        是否使用到 2i 索引; 默认为 :const:`False`.

        子类如果使用到 2i, 需要把这里设置成 :const:`True`, 并实现
        :meth:`._do_sync_2i` 方法.


.. vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
