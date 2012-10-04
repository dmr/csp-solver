#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='Csp-Solver',
    version='0.4',
    url='https://github.com/dmr/csp-solver',
    license='MIT',
    author='Daniel Rech',
    author_email='danielmrech@gmail.com',
    description=(
        'A wrapper library for python to solve a Constraint '
        'Satisfaction Problem with sugar '
        '(http://bach.istc.kobe-u.ac.jp/sugar/) and minisat2 '
        '(http://minisat.se/MiniSat.html)'),
    long_description=open('README.md').read(),
    py_modules= ['csp_solver'],

    entry_points={
        'console_scripts': [
            'csp_solver = csp_solver:main',
        ],
    },

    install_requires=[
        'argparse',
        'which',
        'subprocess32',

        'spec' # for tests
    ],

    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],
)
