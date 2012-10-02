# -*- coding: utf-8 -*-
import unittest


def test_csp_solver_is_installed():
    import csp_solver
    assert csp_solver.do_solve


import os
import argparse

from csp_solver import (do_solve, get_parser, weighted_sum_to_csp,
                        get_valid_csp_solver_config,
                        solve_csp)


csp_solver_config = get_valid_csp_solver_config(
    sugarjar_path=os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            'sugar-v1-15-0.jar'
        )
    )
)


class TestBasicScenarios(unittest.TestCase):
    def test_not_satisfiable(self):
        result = do_solve(
            variables=[[1,2], [1,2]],
            reference_value=5,
            csp_solver_config=csp_solver_config
        )
        assert result['satisfiable_bool'] == False, \
            result['satisfiable_bool']
        # is not a minisat result, sugar returns that!
        assert result['solution_list'] == None, result['solution_list']
        # minisat returns (None, None, None)

    def test_is_satisfiable1(self):
        result = do_solve(
            variables=[[1,2]],
            reference_value=1,
            csp_solver_config=csp_solver_config
        )
        assert ('satisfiable_bool' in result and
                result['satisfiable_bool'] == True), result
        assert result['solution_list'] == [1], result
        # (True, [1], '0.000595')

    def test_is_satisfiable2(self):
        result = do_solve(
            variables=[[1,2], [1,2]],
            reference_value=4,
            csp_solver_config=csp_solver_config
        )
        assert result['satisfiable_bool'] == True
        assert result['solution_list'] == [2, 2]
        # (True, [2, 2], '0.000599')

    def test_is_satisfiable3(self):
        result = do_solve(
            variables=[
                [-1, 0, 1], [-1,-2,-3], [-1, 0, 1], [-1,-2,-3]
            ],
            reference_value=0,
            csp_solver_config=csp_solver_config
        )
        assert result['satisfiable_bool'] == True
        assert result['solution_list'] == [1, -1, 1, -1]
        # (True, [1, -1, 1, -1], '0.000659')

    def test_is_satisfiable4(self):
        result = do_solve(
            variables=[
                [1,2], [-1,-2,-3], [1,2,3], [-1,-2,-3], [1,2,3],
                [-1,-3,-2], [1,2,3], [-1,-2,-3],
            ],
            reference_value=0,
            csp_solver_config=csp_solver_config
        )
        assert result['satisfiable_bool'] == True
        assert result['solution_list'] == [2, -3, 1, -1, 2, -3, 3, -1]
        # (True, [2, -3, 1, -1, 2, -3, 3, -1], '0.000856')

    def test_is_satisfiable_big_problem(self):
        actors_40 = [[1,2] for i in range(20)]
        actors_40.extend([[-1,-2,-3] for i in range(20)])
        result = do_solve(
            variables=actors_40,
            reference_value=0,
            csp_solver_config=csp_solver_config
        )
        assert result['satisfiable_bool'] == True
        assert result['solution_list'] == [-1, -1, -1, -3, 2,
           -3, -1, -1, -3, -1, -1, 2, 1, 2, 1, 2, 2, 1, 2, 2,
           -1, -3, -3, -1, 2, 2, -1, -1, -3, -1,
           2, 2, 2, 1, 2, 1, 1, 2, -1, -3], result['solution_list']

    def test_is_satisfiable_bigger_problem(self):
        actors_400 = [[1,2] for i in range(200)]
        actors_400.extend([[-1,-2,-3] for i in range(200)])
        result = do_solve(
            variables=actors_400,
            reference_value=0,
            csp_solver_config=csp_solver_config
        )
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


class TestCliParser(unittest.TestCase):
    def test_raises_error_if_missing_args(self):
        parser = get_parser()
        self.failUnlessRaises(
            SystemExit,
            parser.parse_args,
            '--csp-file a -c b -k -t r'.split()
        )

    def test_works_if_input_ok(self):
        parser = get_parser()

        parsed_args = parser.parse_args(
            '--csp-file a -c b -k -t r '
            '--sugar-jar sugar-v1-15-0.jar'.split()
        )

        expected_result = argparse.Namespace(
            csp_file=['a', 'b'],
            keep_tmpfiles=True,
            minisat=None,
            sugar_jar='sugar-v1-15-0.jar',
            tmp_folder='r',
        )
        assert parsed_args == expected_result, parsed_args


def test_weighed_sum_problem_gets_converted_to_csp():
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


class TestSolveCsp(unittest.TestCase):
    def test_passes_and_returns_expected_result(self):
        result = solve_csp(
            csp_file=os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                'simple_example.csp')),
            remove_tmp_files=True,
            csp_solver_config=csp_solver_config
        )
        self.failUnlessEqual(len(result),2)
        print result[0]

        assert set(result[1].keys()) == \
            set([
                'minisat_cpu_time',
                'csp_to_cnf_time',
                'minisat_time',
                'map_file_size',
                'solution_list',
                'satisfiable_bool',
                'cnf_file_size'
            ])



def test_minisat_is_deterministic():
    for _ in range(20):
        result = do_solve(
            variables=[
                [-1, 0, 1], [-1, 0, 1], [-1, 0, 1], [-1, 0, 1],
            ],
            reference_value=0,
            quiet=False,
            csp_solver_config=csp_solver_config
        )

        # possible solutions:
        #[0,0,0,0], [-1,-1,1,1]...
        assert result['satisfiable_bool'] == True
        assert result['solution_list'] == [0, -1, 0, 1], \
            result['solution_list']
        # (True, [1, -1, 1, -1], '0.000659')
