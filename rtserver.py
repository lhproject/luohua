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

    server.cli_server(
            'socketio',
            listen=(listen_conf['host'], listen_conf['port']),
            resource='socket.io',
            policy_server=policy_conf['enabled'],
            policy_listener=(policy_conf['host'], policy_conf['port']),
            )


if __name__ == '__main__':
    main()


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
