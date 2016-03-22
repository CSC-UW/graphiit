#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# setup.py

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

setup(
    name='graphite',
    version='0.0.1',
    description='Python library for building PyPhi network graphs',
    author='Graham Findlay',
    url='http://github.com/grahamfindlay/pyphi',
    license='GNU General Public License v3.0',
    install_requires=['numpy', 'pyphi', 'networkx']
)
