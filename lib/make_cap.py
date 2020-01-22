"""
This script takes jinja2 templates in `templates` and converts them into code files in `lib`.
"""
import jinja2
import json
import os
import sys
import collections

LIB_DIR = os.path.dirname(os.path.abspath(__file__))
CYPPY_DIR = os.path.join(LIB_DIR, '../cyppy')

sys.path.append(CYPPY_DIR)
import read_meta

CAP_BASENAME = 'physics_cap.F90'
FORTRAN_DIR = os.path.join(LIB_DIR, 'test')
CAP_OUT_FILENAME = os.path.join(FORTRAN_DIR, CAP_BASENAME)

all_templates = ('physics_data.F90', '_wrapper.pyx', 'dynamics_data.F90')


def get_module_list(scheme_list):
    module_dict = collections.defaultdict(list)
    for routine in read_meta.iterate_routines(scheme_list):
        module_name, extension = routine.filename.split('.')
        module_dict[module_name].append(routine.name)
    module_list = []
    for module_name, routine_list in module_dict.items():
        module_list.append({'name': module_name, 'members': routine_list})
    return module_list


def get_routine_list(scheme_list):
    routine_list = []
    standard_name_to_name = read_meta.get_standard_name_to_name(scheme_list)
    for routine in read_meta.iterate_routines(scheme_list):
        arg_list = get_arg_list(routine, standard_name_to_name)
        arg_list = arg_list[:-2]  # skip errmsg, errflg as these are added manually
        routine_list.append(
            {
                'name': routine.name,
                'args': arg_list,
                'arg_names': [arg['name'] for arg in arg_list],
            }
        )
    return routine_list


def get_type_string(arg_type, arg_kind):
    if arg_kind is None:
        return arg_type
    else:
        return f"{arg_type}(kind={arg_kind})"


def get_arg_list(routine, standard_name_to_name):
    arg_list = []
    for arg in routine.args:
        arg_dict = {
            "type": get_type_string(arg.type, arg.kind),
            "intent": arg.intent,
            "name": arg.name,
        }
        if len(arg.dimensions) > 0:
            var_names = [standard_name_to_name[std_name] for std_name in arg.dimensions]
            arg_dict['dimensions'] = f"({', '.join(var_names)})"
        else:
            arg_dict['dimensions'] = ''
        arg_list.append(arg_dict)
    return arg_list


if __name__ == '__main__':
    scheme_list = read_meta.load_meta_dir(FORTRAN_DIR)

    template_dir = os.path.join(LIB_DIR, 'templates')
    template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
    template_env = jinja2.Environment(loader=template_loader, autoescape=True)

    cap_template = template_env.get_template(CAP_BASENAME)
    result = cap_template.render(
        module_list=get_module_list(scheme_list),
        routine_list=get_routine_list(scheme_list),
    )
    with open(CAP_OUT_FILENAME, 'w') as f:
        f.write(result)
