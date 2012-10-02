Csp-Solver
==========

A wrapper library for python to solve a Constraint Satisfaction Problem with sugar (http://bach.istc.kobe-u.ac.jp/sugar/) and minisat2 (http://minisat.se/MiniSat.html)


Installation
------------

Csp-Solver can be installed via pip from this repository.

    pip install git+http://github.com/dmr/csp-solver.git#egg=csp-solver

In addition to the python package, an installation of minisat2 is needed in PATH (or passed to CLI).
minisat2 can be retreived from https://github.com/niklasso/minisat.git.

To install minisat with user rights on a standard linux system you can use:

    make minisat

available in https://github.com/dmr/csp-solver/blob/master/Makefile.

Test the installation

    wget http://github.com/dmr/csp-solver/raw/master/tests/simple_example.csp
    wget http://github.com/dmr/csp-solver/raw/master/tests/sugar-v1-15-0.jar
    csp_solver.py -c simple_example.csp --sugar-jar sugar-v1-15-0.jar


Development
-----------

    git clone http://github.com/dmr/csp-solver.git
    cd csp-solver
    python setup.py test
    python setup.py develop


Credits
-------

The real work here was done by the development teams of sugar (http://bach.istc.kobe-u.ac.jp/sugar/) and minisat2 (https://github.com/niklasso/minisat.git). Thank you for your work!
