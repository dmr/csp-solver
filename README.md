csp_solver
==========

A wrapper library for python to solve a Constraint Satisfaction Problem with sugar (http://bach.istc.kobe-u.ac.jp/sugar/) and minisat2 (http://minisat.se/MiniSat.html)


Installation
============

1. Install envoy development version
   pip install git+https://github.com/kennethreitz/envoy.git#egg=envoy
2. get the latest version of minisat2 from https://github.com/niklasso/minisat.git and compile it
3. Download the latest version of sugar (tested for v1.15.0) from http://bach.istc.kobe-u.ac.jp/sugar/
4. Install this package
   pip install git+https://github.com/dmr/constraint_satisfaction_solver.git#egg=csp_solver


Notes
=====

Current, the implementation is only tested on Mac OS X 10.7.4.
Maybe, I'll add support for other systems later.