#!/bin/sh
# XXX: 一定要设置 $LH_{KEY,CERT}FILE 变量, 否则命令语法就不对了!
exec gunicorn -w2 -k gevent --keyfile "${LH_KEYFILE}" --certfile "${LH_CERTFILE}" -b 127.0.0.1:9090 luohua.app.wsgi
