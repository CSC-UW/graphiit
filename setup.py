#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# setup.py

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='graphiit',
    version='0.1.0',
    author='Graham Findlay',
    url='http://github.com/grahamfindlay/graphiit',
    description='Python library for building PyPhi network graphs',
    long_description=readme,
    license='GNU General Public License v3.0',
    install_requires=[
        'numpy',
        'pyphi>=1.0.0',
        'networkx<2.0.0'],
    packages=['graphiit'],
    include_package_data=True,
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
