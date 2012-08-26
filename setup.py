#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='Csp-Solver',
    version='0.1.1',
    url='https://github.com/dmr/csp-solver',
    license='MIT',
    author='Daniel Rech',
    author_email='danielmrech@gmail.com',
    description='',
    long_description=__doc__,
    py_modules= ['csp_solver'],
    scripts=['csp_solver.py'],
    install_requires=['argparse'],
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
    ],

    tests_require=['Attest'],
    test_loader='attest:auto_reporter.test_loader',
    test_suite='tests.csp_test'
)