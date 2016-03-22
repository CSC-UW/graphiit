#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# setup.py

try:
  from setuptools import setup
except ImportError:
  from distutils.core import setup

setup(
    name='graphiit',
    version='0.0.1',
    description='Python library for building PyPhi network graphs',
    author='Graham Findlay',
    url='http://github.com/grahamfindlay/graphiit',
    license='GNU General Public License v3.0',
    install_requires=['numpy', 'pyphi', 'networkx'],
    packages=['graphiit'],
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Natural Language :: English',
      'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
      'Programming Language :: Python',
      'Programming Language :: Python :: 3',
      'Topic :: Scientific/Engineering',
    ]
)
