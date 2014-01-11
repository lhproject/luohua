#!/bin/bash

PROJECT_ROOT="$( cd "$( dirname ${BASH_SOURCE[0]} )" && pwd )"

ORGANIZATION="JNRain"
INCEPTION_YEAR=2013
THIS_YEAR="$( date "+%Y" )"

if [[ "${THIS_YEAR}" == "${INCEPTION_YEAR}" ]]; then
    COPYRIGHT_YEAR=${INCEPTION_YEAR} ;
else
    COPYRIGHT_YEAR="${INCEPTION_YEAR}-${THIS_YEAR}" ;
fi

# sed address to the copyright line
# 版权行的 sed 地址
COPYRIGHT_LINE_NUMBER="5"

# format of copyright line, in sed pattern syntax
# 版权行的格式, 使用 sed 正则语法
NEW_COPYRIGHT_LINE="# Copyright (C) ${COPYRIGHT_YEAR} ${ORGANIZATION}"

SED_COMMAND="${COPYRIGHT_LINE_NUMBER}c\\
${NEW_COPYRIGHT_LINE}
;"


# execute on all .py files
# 在所有 .py 文件上执行
find "${PROJECT_ROOT}/luohua" -name '*.py' -type f | xargs sed -i -s "${SED_COMMAND}"


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
