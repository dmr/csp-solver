#!/usr/bin/env python

import functools
import hashlib
import os
import subprocess
import time


def time_diff(func):
    @functools.wraps(func)
    def with_time_diff(*args, **kwargs):
        from time import time as _tme
        b = _tme()
        ret_val = func(*args, **kwargs)
        return _tme()-b, ret_val
    return with_time_diff


def unique_hash(unique_string):
    hash = hashlib.sha1()
    hash.update(unique_string)
    return hash.hexdigest()


get_file_size = lambda file_name: os.stat(file_name).st_size


def check_minisat_and_sugar_exist(
        minisat_path=os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'minisat')),
        sugarjar_path = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 'sugar-v1-15-0.jar'))
    ):
    assert os.path.exists(minisat_path), \
        "Please pass existing minisat executable"
    assert os.path.exists(sugarjar_path), \
        "Please pass existing sugar.jar"
    return minisat_path, sugarjar_path


def weighted_sum_to_csp(variables, reference_value):
    # (domain D1 (1 2 3))
    domain_tmpl = "(domain {domain_name} ({domain_values}))"

    # (int V1 D1)
    variable_tmpl = "(int {variable_name} {domain_name})"

    # (weightedsum ( ( 1 V1 ) ( 1 V2 ) ( 1 V3 ) ( 1 V4 )) eq 1)
    constraint_tmpl = "(weightedsum ( {variables_str} ) eq {the_sum})"

    result_domains = {} # frozenset([1,2,3]): 'R1'
    result_variables = {}

    for variable in variables:
        cleaned_variable = frozenset(variable)
        if cleaned_variable in set(result_domains.keys()):
            domain_name = result_domains[cleaned_variable]
        else:
            domain_name = 'D{0}'.format(len(result_domains)+1)
            result_domains[cleaned_variable] = domain_name

        variable_name = 'V{0}'.format(len(result_variables)+1)
        result_variables[variable_name] = domain_name

    return "\n".join(
        domain_tmpl.format(
            domain_name=domain_name,
            domain_values=" ".join(str(v) for v in domain_values)
        ) for domain_values, domain_name in result_domains.items()
    ) + \
    '\n' + "\n".join(
        variable_tmpl.format(
            variable_name=variable_name,
            domain_name=domain_name
        ) for variable_name, domain_name in result_variables.items()
    ) + \
    "\n" + constraint_tmpl.format(
        variables_str=' '.join(['( 1 %s )' % var_name
            for var_name in result_variables.keys()]),
        the_sum=reference_value
    )


@time_diff
def solve_csp(csp_file,
              tmp_folder,
              remove_tmp_files,

              unique_repr=None,
              quiet=True,

              minisat_path=None, sugarjar_path=None
    ):

    if unique_repr is None:
        config_hash = unique_hash(csp_file)
        unique_repr = '{1}_2'.format(config_hash, time.time())

    minisat_path, sugarjar_path = check_minisat_and_sugar_exist(
        minisat_path, sugarjar_path)

    tmp_folder = os.path.abspath(tmp_folder)

    assert os.path.exists(tmp_folder), ('Please create and pass a folder '
                                        'for temporary files.')

    # 2. .csp -> CNF
    cnf_file = os.path.join(tmp_folder, u'{0}.cnf'.format(unique_repr))
    map_file = os.path.join(tmp_folder, u'{0}.map'.format(unique_repr))

    # ram://1048576 -> 512MB --> 600 Actors range_size 15
    # CNF needs more than 512 MB!

    sugar_encode_cmd = ['java', u'-jar', sugarjar_path,
                        u'-encode', csp_file, cnf_file, map_file]
    b = time.time()
    sugar_encode_resp_std_out = subprocess.check_output(sugar_encode_cmd)
    csp_to_cnf_time = time.time() - b

    result = {
        'csp_to_cnf_time':csp_to_cnf_time
    }

    if sugar_encode_resp_std_out:
        if not quiet:
            print "sugar reported UNSATISFIABLE"

        assert sugar_encode_resp_std_out == 's UNSATISFIABLE\n', \
                sugar_encode_resp_std_out
        result['satisfiable_bool'] = False
        result['solution_list'] = None

    else:
        result['cnf_file_size'] = get_file_size(cnf_file)
        result['map_file_size'] = get_file_size(map_file)
        if not quiet:
            print "cnf file size:", result['cnf_file_size']
            print "map file size:", result['map_file_size']

        out_file = os.path.join(tmp_folder,
            '{0}.out'.format(unique_repr))

        # 3. execute minisat2/solve.
        # 800 Actors range_size 15 needs more than 2GB memory!
        minisat_cmd = [minisat_path, '-verbosity=0', cnf_file, out_file]
        b = time.time()
        minisat_resp = subprocess.check_output(
            minisat_cmd, stderr=subprocess.STDOUT)
        result['minisat_time'] = time.time() - b

        solvable_bool = minisat_resp.splitlines()[-1]
        if solvable_bool == 'SATISFIABLE':
            if not quiet:
                print "minisat reported SATISFIABLE"
                # minisat prints statistics to std_err
                print minisat_resp

            result['satisfiable_bool'] = True

            def get_cpu_time(minisat_resp):
                third_last_line = minisat_resp.splitlines()[-3:-2][0]
                return float(third_last_line.split()[-2:-1][0])
            result['minisat_cpu_time'] = get_cpu_time(minisat_resp)
            #TODO: convert to timedelta?

            # calculate and show result
            sugar_decode_cmd = [
                'java', '-jar',
                sugarjar_path, '-competition', '-decode',
                out_file, map_file]
            decode_result = subprocess.check_output(sugar_decode_cmd)
            assert decode_result, "Decode should return text"
            if not quiet:
                print decode_result

            # second way to check if satisfiable
            #last_word_of_first_line = stdout.split('\n')[0].split()[1]
            #if last_word_of_first_line == 'SATISFIABLE':

            last_line_without_first_letter = decode_result.\
                splitlines()[1].split()[1:]
            result['solution_list'] = [int(r)
                for r in last_line_without_first_letter]

            if remove_tmp_files:
                os.remove(out_file)

        else:
            print "minisat reported UNSATISFIABLE"

            result['satisfiable_bool'] = False
            result['solution_list'] = []

        if remove_tmp_files:
            os.remove(cnf_file)
            os.remove(map_file)

    return result


def do_solve(variables, reference_value, tmp_folder,
             remove_tmp_files=True, quiet=True,

             minisat_path=None, sugarjar_path=None
             ):

    minisat_path, sugarjar_path = check_minisat_and_sugar_exist(
        minisat_path, sugarjar_path)

    assert os.path.exists(tmp_folder), ('Please create and pass a folder '
                                        'for temporary files.')

    b = time.time()
    csp_content = weighted_sum_to_csp(variables=variables,
                                   reference_value=reference_value)

    # one step after another
    config_hash = unique_hash(csp_content)
    unique_repr = '{1}_2'.format(config_hash, time.time())

    csp_file = os.path.join(tmp_folder, '{0}.csp'.format(unique_repr))
    assert not os.path.exists(csp_file)

    with open(csp_file, 'wb') as csp_fp:
        csp_fp.write(csp_content)
    create_csp_time = time.time() - b

    result = {
        'create_csp_time':create_csp_time,
        'csp_file_size':get_file_size(csp_file)
    }

    solve_csp_time, solve_csp_result = solve_csp(csp_file=csp_file,
                     unique_repr=unique_repr,
                     tmp_folder=tmp_folder,
                     remove_tmp_files=remove_tmp_files, quiet=quiet,
                     minisat_path=minisat_path,
                     sugarjar_path=sugarjar_path)

    result.update(solve_csp_result)

    if not quiet:
        print "Operating system overhead:", solve_csp_time, \
            result['minisat_time'] if 'minisat_time' in result else ''
    result['overall_solve_csp_time'] = solve_csp_time

    if remove_tmp_files:
        os.remove(csp_file)

    return result


def add_config_params_to_argparse_parser(parser):
    parser.add_argument('-t','--tmp-folder', action="store",
        type=str, help=('Location of folder for temporary files. '
                        'Should be on a RAM-disk for performance'))
    parser.add_argument('--minisat', action="store",
        type=str, default='.', help="minisat2 binary to use")
    parser.add_argument('--sugar-jar', action="store",
        type=str, default='.', help="sugar.jar to use")
    return parser


def get_parser():
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--csp-file', action="append",
                        type=str, help="CSP file", required=True)

    parser.add_argument('-k','--keep-tmpfiles',
        action="store_true", default=False,
        help="Temporary files are stores after program execution")

    return add_config_params_to_argparse_parser(parser)


def get_valid_csp_solver_config(minisat_path, sugarjar_path, tmp_folder=None):
    if tmp_folder:
        folder = os.path.abspath(tmp_folder)
        if not os.path.exists(folder):
            raise Exception("Please pass existing tmp-folder, '%s'"
                            "does not exist" % folder)
    else:
        import tempfile
        folder = tempfile.gettempdir()

    if not minisat_path:
        raise Exception('Please pass path of the minisat binary')
    minisat_path = os.path.abspath(minisat_path)
    if not os.path.exists(minisat_path):
        raise Exception("minisat binary does not exist: %s"
            % minisat_path)

    if not sugarjar_path:
        raise Exception('Please pass path of the sugar.jar binary')
    sugarjar_path = os.path.abspath(sugarjar_path)
    if not os.path.exists(sugarjar_path):
        raise Exception("sugar.jar binary does not exist: %s"
        % sugarjar_path)

    return dict(
        minisat_path=minisat_path,
        sugarjar_path=sugarjar_path,
        tmp_folder=folder
    )


if __name__ == '__main__':
    parser = get_parser()
    import sys
    parsed_args = parser.parse_args(sys.argv[1:])

    csp_solver_config = get_valid_csp_solver_config(parsed_args.minisat,
        parsed_args.sugar_jar, parsed_args.tmp_folder)

    for csp_file in parsed_args.csp_file:
        print ">>> Processing",csp_file
        assert os.path.isfile(csp_file)
        csp_file = os.path.abspath(csp_file)
        unique_repr = u'{0}_{1}'.format(
            os.path.basename(csp_file), #split path
            time.time())
        solve_csp_time, result = solve_csp(csp_file=csp_file,
               unique_repr=unique_repr,
               remove_tmp_files=not parsed_args.keep_tmpfiles,
               quiet=True,
               **csp_solver_config
        )
        print "SATISFIABLE" if result.pop('satisfiable') \
            else "UNSATISFIABLE!", 'Took', solve_csp_time
        import pprint
        pprint.pprint(result)
        print
