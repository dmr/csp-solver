Csp-Solver
==========

A wrapper library for python to solve a Constraint Satisfaction Problem with sugar (http://bach.istc.kobe-u.ac.jp/sugar/) and minisat2 (http://minisat.se/MiniSat.html)



Notes
=====

Current, the implementation is only tested on Mac OS X 10.7.4.
Maybe, I'll add support for other systems later.



Installation
------------

Csp-Solver can be installed via pip from this repository. It's not on Pypi yet because it only supports Mac OS X and is still only a development version.

    1. Clone this repository && cd csp-solver
    2. python setup.py test
    3. python setup.py develop


Known issues
------------

Csp-Solver is provided with a version of minisat2 (https://github.com/niklasso/minisat.git) and
sugar (v1.15.0, from http://bach.istc.kobe-u.ac.jp/sugar/).
These work on my computer but they might not work on yours. If the tests fail, build your own minisat2 version and connect them in the test files.
