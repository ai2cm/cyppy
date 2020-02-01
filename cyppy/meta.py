import configparser
import collections
from collections import namedtuple
from typing import Sequence, Dict, List
import io
import os

ENTRY_HEADER = '[ccpp-arg-table]'
INTENT_VALUES = ('in', 'out', 'inout')
BOOL_VALUES = ('T', 'F')

# These derived types will not be loaded, and shemes using them will also be ignored.
# This is because we haven't implemented wrapping/packing/unpacking these types yet.
IGNORED_TYPES = [
    # these types contain non-pointer array attributes
    'GFS_control_type',
    'GFS_data_type',
    'GFS_init_type',
    'topfsw_type',
    'topflw_type',
    'sfcfsw_type',
    'sfcflw_type',
    # these are all other GFS containers, disabled to test non-packing routines only
    'GFS_statein_type',
    'GFS_stateout_type',
    'GFS_sfcprop_type',
    'GFS_coupling_type',
    'GFS_grid_type',
    'GFS_tbd_type',
    'GFS_cldprop_type',
    'GFS_radtend_type',
    'GFS_diag_type',
    'GFS_interstitial_type',
    # need to implement special wrapping for character type
    'character',
]

BaseRoutine = namedtuple("Routine", ["name", "args", "internal_args", "types"])


# subclass to set default assumption that no derived types are used
class Routine(BaseRoutine):

    def __new__(cls, name, args, internal_args=None, types=None):
        if internal_args is None:
            internal_args = args
        if types is None:
            types = ()
        return super(Routine, cls).__new__(cls, name, args, internal_args, types)


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
Module = namedtuple("Module", ["name", "members"])
DerivedDataType = namedtuple("DerivedDataType", ["name", "attrs"])
Attribute = namedtuple(
    "Attribute",
    ["name", "standard_name", "long_name", "units", "dimensions", "type", "kind"]
)
CCPPMetadata = namedtuple("CCPPMetadata", ["modules", "schemes", "types"])


def remove_ignored_schemes(schemes):
    return_list = []
    for scheme in schemes:
        for routine in scheme.init, scheme.run, scheme.finalize:
            if ignore_routine(routine):
                break
        else:
            return_list.append(scheme)
    return tuple(return_list)


def remove_ignored_derived_types(derived_types):
    return tuple([
        ddt for ddt in derived_types if ddt.name not in IGNORED_TYPES
    ])


def remove_ignored_members(members):
    return_list = []
    for member in members:
        if hasattr(member, 'args') and ignore_routine(member):
            pass
        elif member.name in IGNORED_TYPES:
            pass
        else:
            return_list.append(member)
    return tuple(return_list)


def ignore_routine(routine):
    for arg in routine.internal_args[:-2]:  # don't consider errmsg, errflg
        if arg.type in IGNORED_TYPES:
            return True
    return False


def get_scheme_module(scheme):
    members = (scheme.init, scheme.run, scheme.finalize)
    return Module(name=scheme.name, members=members)


def get_module_name(filename):
    filename = os.path.basename(filename)
    if '.' in filename:
        module_name = filename[:filename.rindex('.')]
    else:
        module_name = filename
    return module_name


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


def fill_missing_routines(scheme_name, routine_dict):
    """
    Make sure a routine_dict for a scheme has 'init' and 'finalize' defined. Assume
    'run' is already defined."""
    for optional_routine in 'init', 'finalize':
        if optional_routine not in routine_dict:
            routine_dict[optional_routine] = Routine(
                name=get_routine_name(scheme_name, optional_routine),
                args=(),
            )


def validate(value, arg_name, key, options):
    if value not in options:
        raise ValueError(
            f"{key} must be one of {options} but {value} was given for {arg_name}"
        )


def validate_dimensions(value, arg_name):
    if not value.startswith('(') or not value.endswith(')'):
        raise ValueError(
            f"dimensions must be encapsulated in parentheses, "
            f"but a value '{value}' was given for {arg_name}"
        )


def get_argument(arg_name, data):
    validate(data['intent'], arg_name, 'intent', INTENT_VALUES)
    validate(data['optional'], arg_name, 'optional', BOOL_VALUES)
    validate_dimensions(data['dimensions'], arg_name)
    return Argument(
        name=arg_name,
        standard_name=data['standard_name'],
        long_name=data['long_name'],
        units=data['units'],
        dimensions=get_dimensions(data['dimensions']),
        type=data['type'],
        kind=data.get('kind', None),
        intent=data['intent'],
        optional=(data['optional'] == 'T')
    )


def get_attribute(name, data):
    validate_dimensions(data['dimensions'], name)
    return Attribute(
        name=name,
        standard_name=data['standard_name'],
        long_name=data['long_name'],
        units=data['units'],
        dimensions=get_dimensions(data['dimensions']),
        type=data['type'],
        kind=data.get('kind', None),
    )


def get_argument_from_attribute(attr: Attribute, intent: str, optional: bool) -> Argument:
    return Argument(
        name=attr.name,
        standard_name=attr.standard_name,
        long_name=attr.long_name,
        units=attr.units,
        dimensions=attr.dimensions,
        type=attr.type,
        kind=attr.kind,
        intent=intent,
        optional=optional
    )


def get_dimensions(dimension_string):
    if dimension_string == '()':
        return ()
    else:
        return tuple(dim.strip() for dim in dimension_string.strip('()').split(','))


def load_meta(filenames):
    scheme_dict = {}
    module_list = []
    type_list = []
    for filename in filenames:
        with open(filename, 'r') as f:
            data = f.read()
        file_module_name = get_module_name(filename)
        for entry_text in [ENTRY_HEADER + d for d in data.split(ENTRY_HEADER)[1:]]:
            config = get_scheme_parser()
            config.read_file(io.StringIO(entry_text))
            if config['ccpp-arg-table']['type'] == 'scheme':
                routine = load_routine(config)
                scheme_name = get_scheme_name(routine.name)
                scheme_dict[scheme_name] = scheme_dict.get(scheme_name, {})
                scheme_dict[scheme_name][get_routine_type(routine.name)] = routine
            elif config['ccpp-arg-table']['type'] == 'module':
                module_list.append(load_module(config))
            elif config['ccpp-arg-table']['type'] == 'ddt':
                type_list.append(load_type(config))
        scheme_list = []
        for scheme_name, routine_dict in scheme_dict.items():
            fill_missing_routines(scheme_name, routine_dict)
            scheme_list.append(
                Scheme(
                    name=scheme_name,
                    **routine_dict
                )
            )
            module_list.append(get_scheme_module(scheme_list[-1]))
    scheme_list = [expand_scheme_derived_args(scheme, type_list) for scheme in scheme_list]
    print([t.name for t in type_list])
    return CCPPMetadata(
        modules=consolidate_modules(module_list),
        schemes=remove_ignored_schemes(scheme_list),
        types=remove_ignored_derived_types(type_list),
    )


def consolidate_modules(modules):
    """Combine any modules with the same name, remove empty modules, and
    remove ignored types."""
    module_dict = collections.defaultdict(list)
    for module in modules:
        if isinstance(module.members, str):
            raise ValueError(
                f"members of module {module.name} should in a tuple but a str was given"
            )
        module_dict[module.name].append(module)
    return_modules = []
    for name, modules_to_combine in module_dict.items():
        members = []
        for module in modules_to_combine:
            members.extend(module.members)
        members = remove_ignored_members(deduplicate_tuple(members))
        if len(members) > 0:
            return_modules.append(
                Module(
                    name=name,
                    members=members,
                )
            )
    return return_modules


def deduplicate_tuple(tuple_in):
    return tuple(sorted(tuple(set(tuple_in))))


def load_type(config):
    attr_list = []
    for attr_name, data in config.items():
        if attr_name not in ('ccpp-arg-table', 'DEFAULT'):  # first item is header info
            attr_list.append(get_attribute(attr_name, data))
    ddt_name = config['ccpp-arg-table']['name']
    ddt = DerivedDataType(
        name=ddt_name,
        attrs=tuple(attr_list),
    )
    return ddt


def load_module(config):
    return Module(
        name=config['ccpp-arg-table']['name'],
        members=tuple(get_attribute(k, v) for k, v in config.items()
                      if k not in ('ccpp-arg-table', 'DEFAULT'))
    )


def load_routine(config):
    print(f"Loading routine {config['ccpp-arg-table']['name']}")
    arg_list = []
    for arg_name, data in config.items():
        if arg_name not in ('ccpp-arg-table', 'DEFAULT'):  # first item is header info
            arg_list.append(get_argument(arg_name, data))
    routine_name = config['ccpp-arg-table']['name']
    routine = Routine(
        name=routine_name,
        args=tuple(arg_list),
    )
    return routine


def expand_scheme_derived_args(scheme: Scheme, derived_types: Sequence[DerivedDataType]) -> Scheme:
    return Scheme(
        name=scheme.name,
        init=expand_routine_derived_args(scheme.init, derived_types),
        run=expand_routine_derived_args(scheme.run, derived_types),
        finalize=expand_routine_derived_args(scheme.finalize, derived_types)
    )


def expand_routine_derived_args(routine: Routine, derived_types: Sequence[DerivedDataType]) -> Routine:
    ddt_lookup = {ddt.name: ddt for ddt in derived_types}
    ddt_used = []
    expanded_args = expand_derived_args(routine.args, ddt_lookup, ddt_used)
    return Routine(
        name=routine.name,
        args=tuple(expanded_args),
        internal_args=routine.internal_args,
        types=tuple(ddt_used + list(routine.types))
    )


def expand_derived_args(
        args: Sequence[Argument],
        ddt_lookup: Dict[str, DerivedDataType],
        ddt_used: List[DerivedDataType]) -> List[Argument]:
    if len(args) == 0:
        return []
    elif args[0].type in ddt_lookup:
        ddt_arg = args[0]
        ddt = ddt_lookup[ddt_arg.type]
        ddt_used.append(ddt)
        expanded_args = []
        for attr in ddt.attrs:
            expanded_args.append(
                get_argument_from_attribute(attr, ddt_arg.intent, ddt_arg.optional)
            )
        return (
            expand_derived_args(expanded_args, ddt_lookup, ddt_used) +
            expand_derived_args(args[1:], ddt_lookup, ddt_used)
        )
    else:
        return [args[0]] + expand_derived_args(args[1:], ddt_lookup, ddt_used)


def load_meta_dir(dirname):
    return load_meta(os.path.join(dirname, fname) for fname in get_meta_files(dirname))


def combine_metadata(ccpp_metadata_list):
    combined = {}
    for attr in "modules", "schemes", "types":
        combined[attr] = []
        for spec in ccpp_metadata_list:
            combined[attr].extend(getattr(spec, attr))
    return CCPPMetadata(**combined)


def iterate_routines(scheme_list):
    for scheme in scheme_list:
        for routine in scheme.init, scheme.run, scheme.finalize:
            yield routine


def get_standard_name_to_name(ccpp_metadata: CCPPMetadata):
    return_dict = {}
    for routine in iterate_routines(ccpp_metadata.schemes):
        for arg in routine.args:
            _update_standard_name(return_dict, arg.standard_name, arg.name)
    for module in ccpp_metadata.modules:
        for member in module.members:
            _update_standard_name(return_dict, member.standard_name, member.name)
    return return_dict


def _update_standard_name(d, standard_name, name):
    if d.get(standard_name, name) != name:
        raise ValueError(
            f'conflicting values {name} and '
            f'{d[standard_name]} given as variable names '
            f'for {standard_name}'
        )
    else:
        d[standard_name] = name
