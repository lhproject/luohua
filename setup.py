#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

# distribute and setuptools have merged since setuptools-0.7,
# so no more distribute_setup stuff here.
# Rest of the script should continue to work without modification.
from setuptools import setup
from setuptools import find_packages

from luohua import __version__

PKG_DIR = os.path.abspath(os.path.dirname(__file__))


setup(
        name='luohua',
        version=__version__,
        description='Backend of next-generation JNRain',
        author='Wang Xuerui',
        author_email='idontknw.wang+pypi@gmail.com',
        license='GPLv3+',
        url='https://github.com/jnrainerds/luohua/',
        download_url='https://github.com/jnrainerds/luohua/releases/',
        packages=find_packages(exclude=['tests', ]),
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'Intended Audience :: Education',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Topic :: Communications',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        ],
        zip_safe=False,
        )


# vim:set ai et ts=4 sw=4 sts=4 fenc=utf-8:
