#!/usr/bin/env python
import functools
import hashlib
import sys
import os
import time
import argparse
import which

# import backport instead of packaged version
try:
    import subprocess32 as subprocess
except ImportError:
    import subprocess


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
def solve_csp(
        csp_file,
        remove_tmp_files,

        csp_solver_config,

        unique_repr=None,
        quiet=True,
        ):

    csp_solver_config = get_valid_csp_solver_config(**csp_solver_config)

    if unique_repr is None:
        config_hash = unique_hash(csp_file)
        unique_repr = '{1}_2'.format(config_hash, time.time())

    tmp_folder = csp_solver_config['tmp_folder']
    sugarjar_path = csp_solver_config['sugarjar_path']
    minisat_path = csp_solver_config['minisat_path']

    # 2. .csp -> CNF
    cnf_file = os.path.join(tmp_folder, '{0}.cnf'.format(unique_repr))
    map_file = os.path.join(tmp_folder, '{0}.map'.format(unique_repr))

    # ram://1048576 -> 512MB --> 600 Actors range_size 15
    # CNF needs more than 512 MB!

    sugar_encode_cmd = [
        'java', '-jar', sugarjar_path,
        '-encode', csp_file, cnf_file, map_file]
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
        minisat_cmd = [minisat_path, cnf_file, out_file]
        b = time.time()

        process = subprocess.Popen(
            minisat_cmd,
            stdout=subprocess.PIPE,stderr=subprocess.PIPE
        )
        minisat_resp, minisat_resp_stderr = process.communicate()
        if process.returncode not in [0, 10]:
            print "Minisat returned {0}".format(process.returncode)
            print minisat_resp_stderr
            print minisat_resp
            raise Exception("Error executing minisat!")

        result['minisat_time'] = time.time() - b

        solvable_bool = minisat_resp.splitlines()[0]
        if solvable_bool == 'SATISFIABLE':
            if not quiet:
                print "minisat reported SATISFIABLE"

            result['satisfiable_bool'] = True

            def get_cpu_time(resp):
                third_last_line = resp.splitlines()[-2:-1][0]
                return float(third_last_line.split()[-2:-1][0])
            result['minisat_cpu_time'] = get_cpu_time(minisat_resp_stderr)
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


def do_solve(
        variables,
         reference_value,
         csp_solver_config,
         remove_tmp_files=True,
         quiet=True,
         ):

    csp_solver_config = get_valid_csp_solver_config(**csp_solver_config)
    tmp_folder = csp_solver_config['tmp_folder']

    if not quiet:
        print "Using tmp folder", tmp_folder

    b = time.time()
    csp_content = weighted_sum_to_csp(
        variables=variables,
        reference_value=reference_value
    )

    # one step after another
    config_hash = unique_hash(csp_content)
    unique_repr = '{1}_2'.format(config_hash, time.time())

    csp_file = os.path.join(tmp_folder, '{0}.csp'.format(unique_repr))
    assert not os.path.exists(csp_file)

    with open(csp_file, 'wb') as csp_fp:
        csp_fp.write(csp_content)
    create_csp_time = time.time() - b

    do_solve_result = {
        'create_csp_time':create_csp_time,
        'csp_file_size':get_file_size(csp_file)
    }

    solve_csp_time, solve_csp_result = solve_csp(
        csp_file=csp_file,
        unique_repr=unique_repr,
        remove_tmp_files=remove_tmp_files,
        quiet=quiet,

        csp_solver_config=csp_solver_config
    )

    do_solve_result.update(solve_csp_result)
    do_solve_result['overall_solve_csp_time'] = solve_csp_time

    if not quiet:
        print "overall_solve_csp_time: {0}".format(
            do_solve_result['overall_solve_csp_time']
            ), \
            'minisat_time: {0}'.format(
                do_solve_result['minisat_time']
                if 'minisat_time' in do_solve_result
                else ''
            )

    if remove_tmp_files:
        os.remove(csp_file)

    return do_solve_result


class ConfigurationException(Exception):
    pass


def get_valid_csp_solver_config(
        sugarjar_path,
        minisat_path=None,
        tmp_folder=None
        ):

    if (not sugarjar_path or
        not os.path.exists(sugarjar_path)):
        raise ConfigurationException(
            "Please pass existing sugar.jar"
        )

    if minisat_path and os.path.exists(minisat_path):
        pass
    else:
        if minisat_path:
            print ("Passed minisat binary does "
                "not exist"),minisat_path, \
                "Trying PATH"
        if os.path.exists('minisat'):
            minisat_path = os.path.abspath('minisat')
        else:
            try:
                minisat_path = which.which("minisat")
            except which.WhichError as exc:
                raise ConfigurationException(
                    "Please pass an existing minisat2 executable "
                    "or install minisat2 as 'minisat' in PATH"
                )

    if tmp_folder:
        folder = os.path.abspath(tmp_folder)
    else:
        import tempfile
        folder = tempfile.gettempdir()
    if not os.path.exists(folder):
        raise ConfigurationException(
            "Please pass existing tmp-folder, '%s'"
            "does not exist" % folder
        )

    return dict(
        minisat_path=minisat_path,
        sugarjar_path=sugarjar_path,
        tmp_folder=folder
    )


def add_csp_config_params_to_argparse_parser(parser):
    parser.add_argument('-t','--tmp-folder', action="store",
        type=str,
        help=('Location of folder for temporary files. '
              'Choose a RAM-disk for performance')
    )
    parser.add_argument('--minisat', action="store",
        type=str,
        help=("minisat2 binary to use, "
              "default: 'minisat' in $PATH")
    )
    parser.add_argument('--sugar-jar', action="store",
        type=str,
        help="sugar.jar to use",
        required=True
    )
    return parser


def get_parser():
    parser = argparse.ArgumentParser()

    def existing_file(file_name):
        msg = "File does not exist: {0}".format(file_name)
        if not file_name:
            raise argparse.ArgumentTypeError(msg)
        if not os.path.exists(file_name):
            raise argparse.ArgumentTypeError(msg)
        if not os.path.isfile(file_name):
            raise argparse.ArgumentTypeError(msg)
        return os.path.abspath(file_name)

    parser.add_argument('-c', '--csp-file',
        action="append",
        type=existing_file, help="CSP file with the problem definition",
        required=True
    )
    parser.add_argument('-k','--keep-tmpfiles',
        action="store_true",
        help="Store result after program execution"
    )

    return add_csp_config_params_to_argparse_parser(parser)


def main(args=sys.argv[1:]):
    parser = get_parser()
    parsed_args = parser.parse_args(args)

    csp_solver_config = get_valid_csp_solver_config(
        minisat_path=parsed_args.minisat,
        sugarjar_path=parsed_args.sugar_jar,
        tmp_folder=parsed_args.tmp_folder
    )

    for csp_file in parsed_args.csp_file:
        print ">>> Processing",csp_file
        unique_repr = u'{0}_{1}'.format(
            os.path.basename(csp_file), #split path
            time.time())
        solve_csp_time, result = solve_csp(
            csp_file=csp_file,
            unique_repr=unique_repr,
            remove_tmp_files=not parsed_args.keep_tmpfiles,
            quiet=True,
            csp_solver_config=csp_solver_config
        )
        print "SATISFIABLE" if result.pop('satisfiable_bool')\
        else "UNSATISFIABLE!", 'Took', solve_csp_time
        import pprint
        pprint.pprint(result)
        print
