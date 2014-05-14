#!/bin/sh

# TODO: 相对脚本位置定位环境配置
source ./dev-environment.sh

exec gunicorn -w2 -k gevent --keyfile "${LH_KEYFILE}" --certfile "${LH_CERTFILE}" -b 127.0.0.1:9090 luohua.app.wsgi
