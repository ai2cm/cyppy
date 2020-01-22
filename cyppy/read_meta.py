import configparser
from collections import namedtuple
import io
import os

SCHEME_HEADER = '[ccpp-arg-table]'

Routine = namedtuple("Routine", ["name", "args", "filename"])
Argument = namedtuple(
    "Argument",
    [
        "name",
        "standard_name",
        "long_name",
        "units",
        "dimensions",
        "type",
        "kind",
        "intent",
        "optional"
    ]
)
Scheme = namedtuple("Scheme", ["name", "init", "run", "finalize"])


def get_meta_files(dirname):
    return [fname for fname in os.listdir(dirname) if fname.endswith('.meta')]


def get_scheme_parser():
    # must disable interpolation to allow percent symbol for units
    return configparser.ConfigParser(interpolation=None)


def get_routine_type(routine_name):
    return routine_name.split('_')[-1]


def get_scheme_name(routine_name):
    return '_'.join(routine_name.split('_')[:-1])


def get_routine_name(scheme_name, routine_type):
    return f"{scheme_name}_{routine_type}"


def fill_missing_routines(scheme_name, routine_dict, filename):
    """
    Make sure a routine_dict for a scheme has 'init' and 'finalize' defined. Assume
    'run' is already defined."""
    for optional_routine in 'init', 'finalize':
        if optional_routine not in routine_dict:
            routine_dict[optional_routine] = Routine(
                name=get_routine_name(scheme_name, optional_routine),
                args=[],
                filename=os.path.basename(filename),
            )


def get_argument(arg_name, data):
    return Argument(
        name=arg_name,
        standard_name=data['standard_name'],
        long_name=data['long_name'],
        units=data['units'],
        dimensions=get_dimension_list(data['dimensions']),
        type=data['type'],
        kind=data.get('kind', None),
        intent=data['intent'],
        optional=(data['optional'] == 'T')
    )


def get_dimension_list(dimension_string):
    if dimension_string == '()':
        return []
    else:
        return [dim.strip() for dim in dimension_string.strip('()').split(',')]


def load_meta(filename):
    with open(filename, 'r') as f:
        data = f.read()
    scheme_dict = {}
    for scheme_text in [SCHEME_HEADER + d for d in data.split(SCHEME_HEADER)[1:]]:
        config = get_scheme_parser()
        config.read_file(io.StringIO(scheme_text))
        arg_list = []
        for arg_name, data in config.items():
            if arg_name not in ('ccpp-arg-table', 'DEFAULT'):  # first item is header info
                arg_list.append(get_argument(arg_name, data))
        routine_name = config['ccpp-arg-table']['name']
        routine_type = get_routine_type(routine_name)
        scheme_name = get_scheme_name(routine_name)
        scheme_dict[scheme_name] = scheme_dict.get(scheme_name, {})
        scheme_dict[scheme_name][routine_type] = Routine(
            name=routine_name,
            args=arg_list,
            filename=os.path.basename(filename),
        )
    return_list = []
    for scheme_name, routine_dict in scheme_dict.items():
        fill_missing_routines(scheme_name, routine_dict, filename)
        return_list.append(Scheme(
            name=scheme_name,
            **routine_dict
        ))
    return return_list


def load_meta_dir(dirname):
    scheme_list = []
    for fname in get_meta_files(dirname):
        scheme_list.extend(load_meta(os.path.join(dirname, fname)))
    return scheme_list


def iterate_routines(scheme_list):
    for scheme in scheme_list:
        for routine in scheme.init, scheme.run, scheme.finalize:
            yield routine


def get_standard_name_to_name(scheme_list):
    return_dict = {}
    for routine in iterate_routines(scheme_list):
        for arg in routine.args:
            return_dict[arg.standard_name] = arg.name
    return return_dict
