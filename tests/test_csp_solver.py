# -*- coding: utf-8 -*-
from attest import Tests

csp_test = Tests()

@csp_test.test
def is_installed():
    import csp_solver
    assert csp_solver.do_solve


import argparse
import datetime
import os
import tempfile
import time

tmp_folder=tempfile.gettempdir()

from csp_solver import (do_solve, get_parser, weighted_sum_to_csp,
                        check_minisat_and_sugar_exist,
                        solve_csp)

folder = os.path.abspath(os.path.join(os.path.dirname(__file__),
                          'test_csp_solver_tmp'))

quiet = False


minisat_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'minisat'))
sugarjar_path = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 'sugar-v1-15-0.jar'))
_m, _s = check_minisat_and_sugar_exist(minisat_path, sugarjar_path)


@csp_test.test
def test_basic_scenarios():
    basic_scenarios(tmp_folder)


def basic_scenarios(folder):
    before = datetime.datetime.now()

    quiet = True

    kw = dict(tmp_folder=folder, quiet=quiet,
              minisat_path=minisat_path, sugarjar_path=sugarjar_path
    )

    result = do_solve(variables=[[1,2]], reference_value=1, **kw)
    assert 'satisfiable_bool' in result and result['satisfiable_bool'] == True, result
    assert result['solution_list'] == [1], result
    # (True, [1], '0.000595')

    result = do_solve(variables=[[1,2], [1,2]], reference_value=4, **kw)
    assert result['satisfiable_bool'] == True
    assert result['solution_list'] == [2, 2]
    # (True, [2, 2], '0.000599')

    result = do_solve(variables=[[1,2], [1,2]], reference_value=5, **kw)
    assert result['satisfiable_bool'] == False, result['satisfiable_bool']
    # is not a minisat result, sugar returns that!
    assert result['solution_list'] == None, result['solution_list']
    # minisat returns (None, None, None)

    result = do_solve(variables=[
            [-1, 0, 1], [-1,-2,-3], [-1, 0, 1], [-1,-2,-3]
    ], reference_value=0, **kw)
    assert result['satisfiable_bool'] == True
    assert result['solution_list'] == [1, -1, 1, -1]
    # (True, [1, -1, 1, -1], '0.000659')

    result = do_solve(variables=[
        [1,2], [-1,-2,-3], [1,2,3], [-1,-2,-3], [1,2,3],
        [-1,-3,-2], [1,2,3], [-1,-2,-3],
    ], reference_value=0, **kw)
    assert result['satisfiable_bool'] == True
    assert result['solution_list'] == [2, -3, 1, -1, 2, -3, 3, -1]
    # (True, [2, -3, 1, -1, 2, -3, 3, -1], '0.000856')

    actors_40 = [[1,2] for i in range(20)]
    actors_40.extend([[-1,-2,-3] for i in range(20)])
    result = do_solve(variables=actors_40, reference_value=0, **kw)
    assert result['satisfiable_bool'] == True
    assert result['solution_list'] == [-1, -1, -1, -3, 2, -3, -1, -1, -3, -1,
       -1, 2, 1, 2, 1, 2, 2, 1, 2, 2, -1, -3, -3, -1, 2, 2, -1, -1, -3, -1,
       2, 2, 2, 1, 2, 1, 1, 2, -1, -3], result['solution_list']

    actors_400 = [[1,2] for i in range(200)]
    actors_400.extend([[-1,-2,-3] for i in range(200)])
    result = do_solve(variables=actors_400, reference_value=0, **kw)
    assert result['satisfiable_bool'] == True
    assert result['solution_list'] == [-1, -1, -1, -1, -3, -1, -1, -3, -1,
       -3, -1, -1, -3, -1, -1, -3, -1, 1, 2, 2, 1, 2, 2, 2, 2, 1, 2, 1, 2, 2,
       1, 2, 1, 2, 2, 1, 2, 2, -3, -1, -1, -3, -1, -1, -1, -1, -3, -1, -3, -1,
       -3, -1, -1, -3, -1, -3, -1, -1, -1, -3, -1, -1, -3, -1, -1, -3, -3, -1,
       -3, -3, 2, 1, 2, 1, 1, 2, 1, 2, 2, 2, 2, -1, -1, 2, 2, 2, 2, -1, 2, 2,
       -1, -1, 1, 2, 2, 2, 2, 1, -1, -1, -1, -1, -3, -1, -1, -1, -1, 2, 2, 2,
       1, 1, 2, 2, 2, 2, 1, -1, -3, -3, -1, -1, -1, -1, -1, -3, -1, -1, -3,
       -1, -1, -3, -1, 2, 2, 1, 2, 1, 2, 2, 1, 2, 2, 2, 1, 2, 1, 1, 2, -3, -1,
       -1, -1, -1, -1, -1, -3, -3, -1, 1, 2, 1, 2, 2, 2, 2, 2, 2, 1, 1, -3,
       -1, -1, -3, -1, -3, -3, -1, -3, -1, -1, -1, -1, -3, 1, 2, 2, 2, 2, 2,
       2, 1, 2, 1, -1, -3, -3, -1, -1, -1, -1, -3, -1, -1, 1, 2, 2, 2, 2, 1,
       1, 2, -1, -1, -1, -3, -1, -3, 2, 1, -3, -1, 1, 2, 2, 2, 2, 1, 2, 2, 1,
       2, -3, -3, -1, -1, -1, -1, 1, 2, 2, 2, 1, 2, 2, 1, 2, 1, 2, 2, 2, 1,
       1, 2, 2, 2, 1, 2, 2, 1, 2, 1, 1, 2, 2, 2, 2, 1, -1, -1, 2, -3, 2, 1,
       1, 2, -1, -3, 2, 2, 2, 2, 1, 2, 2, 1, 2, 2, 2, 1, -1, -1, -3, -1, -1,
       -1, -1, -3, -1, -3, -3, -1, -3, -1, -1, -1, 2, 2, 1, 2, 2, 1, 2, 2, 1,
       2, 2, 2, 2, 1, 2, 2, 1, 2, 2, 1, 2, -1, -3, -3, -1, -1, -1, -1, -3,
       -3, -1, -3, -3, -1, -1, -1, -3, -1, -1, -3, -1, -1, -1, -3, -3, -1,
       -3, -1, -1, -1, -1, -1, -3, -1, -1, -3, 1, -3, -1, -1, -1, -1, 2, -3,
       2, 2, 1, 2, 2, 1, 2, 2, -1, 1, -1, -1, -1, -3, -1, -3, -3, -1, 1, 2,
       2, 1, 2, 2, 1, 2, 2, 1, -1, -3], result['solution_list']
    #'0.138674'
    print "took", datetime.datetime.now() - before


@csp_test.test
def test_parser():
    parser = get_parser()
    def test_args(arg_string, expected_result):
        assert parser.parse_args(arg_string) == expected_result, \
            parser.parse_args(arg_string)

    test_args('--csp-file a -c b -k -t r'.split(),
              argparse.Namespace(
                csp_file=['a', 'b'], keep_tmpfiles=True, tmp_folder='r',
                minisat=None, sugar_jar=None
              )
    )

    # TODO: test more


@csp_test.test
def test_weighed_sum_problem():
    for args, expected_result in [
        (
            ([
                 [1,2,3],
                 [1,2,3],
                 [-4,-5]
             ], 0), (
                "(domain D2 (-5 -4))\n(domain D1 (1 2 3))\n"
                "(int V1 D1)\n(int V2 D1)\n(int V3 D2)\n"
                "(weightedsum ( ( 1 V1 ) ( 1 V2 ) ( 1 V3 ) ) eq 0)"
                )
            ),
    ]:
        assert weighted_sum_to_csp(*args) == expected_result, \
            "\n{0}\n!=\n{1}\n!".format(
                weighted_sum_to_csp(*args), expected_result
            )


@csp_test.test
def test_do_solve():
    solve_csp(
        csp_file=os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'simple_example.csp')),
        tmp_folder=tmp_folder,
        remove_tmp_files=True,
        minisat_path=minisat_path, sugarjar_path=sugarjar_path
    )


try:
    import ramdisk_mounter

    def test_basic_scenarios_with_ramdisk_mounter():
        with ramdisk_mounter.ramdisk(folder=tmp_folder) as folder:
            basic_scenarios(folder)

    def test_if_minisat_is_deterministic():
        with ramdisk_mounter.ramdisk(folder=tmp_folder) as folder:
            for _ in range(10):
                b = time.time()
                result = do_solve(
                    variables=[
                        [-1, 0, 1], [-1, 0, 1], [-1, 0, 1], [-1, 0, 1],
                    ],
                    reference_value=0,
                    tmp_folder=folder, quiet=quiet,
                    minisat_path=minisat_path, sugarjar_path=sugarjar_path
                )
                print "Took:",time.time() - b

                # possible solutions:
                #[0,0,0,0], [-1,-1,1,1]...
                assert result['satisfiable_bool'] == True
                assert result['solution_list'] == [0, -1, 0, 1], result['solution_list']
                # (True, [1, -1, 1, -1], '0.000659')

    csp_test.test(test_basic_scenarios_with_ramdisk_mounter)
except ImportError:
    print "Install https://github.com/dmr/ramdisk_mounter.git for faster CSP results"


if __name__ == '__main__':
    csp_test.run()