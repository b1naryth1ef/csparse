#!/usr/bin/env python

import os
import sys

import csparse

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

packages = [
    'csparse',
]

requires = [
]

setup(
    name='csparse',
    version=csparse.__version__,
    description='a csgo demo parser',
    long_description='',
    author='Andrei',
    author_email='andrei.zbikowski@gmail.com',
    url='http://github.com/b1naryth1ef/csparse',
    packages=packages,
    package_data={},
    package_dir={'csparse': 'csparse'},
    include_package_data=True,
    install_requires=requires,
    license='Apache 2.0',
    zip_safe=False,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ),
)
