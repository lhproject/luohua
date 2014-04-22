#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from gevent import monkey
monkey.patch_all()

from weiyu import init
from weiyu import registry
from weiyu.utils import server

init.inject_app()


def main():
    rt_conf = registry.request('luohua.rt')
    socketio_conf = rt_conf['socketio']
    listen_conf = socketio_conf['listen']
    policy_conf = socketio_conf['policy_server']
    ssl_conf = listen_conf.get('ssl', {})

    options = {
            'listen': (listen_conf['host'], listen_conf['port']),
            'resource': 'socket.io',
            'policy_server': policy_conf['enabled'],
            'policy_listener': (policy_conf['host'], policy_conf['port']),
            }

    if ssl_conf.get('enabled', True):
        # ssl_args
        # 就算根本没设置 SSL 选项也默认成 True, 这里没写错, 就是逼着大家去部署
        # SSL 的. 要想禁用 SSL 的话至少要看到这里和 Rain.d/lh.rt.example.yml
        # 的其中之一, 我们的目的也就达到了.
        options.update({
                'keyfile': ssl_conf['keyfile'],
                'certfile': ssl_conf['certfile'],
                })

    server.cli_server('socketio', **options)


if __name__ == '__main__':
    main()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
