import subprocess
from xml.dom import minidom


def weighted_sum_to_xcsp(allowed_ranges, reference_value):
    doc = minidom.Document()
    instance = doc.createElement("instance")
    doc.appendChild(instance)

    presentation = doc.createElement("presentation")
    presentation.setAttribute("maxConstraintArity", "2")
    presentation.setAttribute("format", "XCSP 2.1")
    presentation.setAttribute("type", "CSP")
    presentation.setAttribute('nbSolutions', '?')
    instance.appendChild(presentation)

    domains = doc.createElement("domains")
    instance.appendChild(domains)

    variables = doc.createElement('variables')
    variables.setAttribute('nbVariables', str(len(allowed_ranges)))
    instance.appendChild(variables)

    all_domains = {} # frozenset([1,2,3]): 'R1'
    global_domain_counter = 0
    global_variable_counter = 0

    all_global_variables = []

    for allowed_range in allowed_ranges:
        global_variable_counter += 1
        variable_name = 'V{0}'.format(global_variable_counter)
        all_global_variables.append(variable_name)

        actor_values = frozenset(allowed_range)
        if actor_values in set(all_domains.keys()):
            domainel_name = all_domains[actor_values]
        else:
            global_domain_counter += 1
            domainel_name = 'D{0}'.format(global_domain_counter)
            all_domains[actor_values] = domainel_name

            domainel = doc.createElement('domain')
            domainel.setAttribute('name', domainel_name)
            domainel.setAttribute('nbValues', str(len(actor_values)))
            domainel.appendChild(doc.createTextNode(' '.join([str(v) for v in actor_values])))
            domains.appendChild(domainel)
            domains.setAttribute('nbDomains', str(len(all_domains.values())))

        variable = doc.createElement('variable')
        variable.setAttribute('name', variable_name)
        variable.setAttribute('domain', domainel_name)
        variables.appendChild(variable)

    constraints = doc.createElement('constraints')
    constraints.setAttribute('nbConstraints', '1')
    instance.appendChild(constraints)

    constraint = doc.createElement('constraint')
    constraint.setAttribute('name', 'C0')
    constraint.setAttribute('arity', '2')
    constraint.setAttribute('reference', 'global:weightedSum')
    constraint.setAttribute('scope', ' '.join(all_global_variables))
    parameters = doc.createElement('parameters')
    parameters.appendChild(doc.createTextNode('[ {0} ]'.format(
        ' '.join(['{ 1 %s }' % var for var in all_global_variables])
    )))
    parameters.appendChild(doc.createElement('eq'))
    parameters.appendChild(doc.createTextNode(' {0}'.format(reference_value)))
    constraint.appendChild(parameters)
    constraints.appendChild(constraint)
    return doc.toprettyxml(indent="    ")


if __name__ == '__main__':

    allowed_ranges = [
        [1,2,3],
        [2,3]
    ]
    reference_value = 3
    xml_file_name = "testfile_unique_name.xml"
    csp_file_name = "testfile_unique_name.csp"
    sugarjar_path = "sugar.jar"

    assert 0, 'please implement arg parsing first'

    import os

    assert not os.path.exists(xml_file_name)
    assert not os.path.exists(csp_file_name)

    # 1. Problem --> XCSP
    xcsp_output = weighted_sum_to_xcsp(allowed_ranges, reference_value)
    with open(xml_file_name, 'w') as f:
        f.write(xcsp_output)

    # 2. XCSP2.1 .xml -> .csp
    std_out = subprocess.check_output(
        ['java','-cp',sugarjar_path,'jp.ac.kobe_u.cs.sugar.XML2CSP',
         xml_file, csp_file_name]
    )
    # 'c 2 domains, 4 variables, 1 predicates, 0 relations, 1 constraints\n'
    if not std_out or std_out.startswith('c '):
        raise Exception("Unknown command output: %s" % std_out)
