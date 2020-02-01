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
import meta

CAP_BASENAME = 'physics_cap.F90'
FORTRAN_DIR = os.path.join(LIB_DIR, 'physics')
CAP_OUT_FILENAME = os.path.join(LIB_DIR, CAP_BASENAME)
INTRINSIC_TYPES = ['integer', 'real', 'logical', 'complex', 'character']

DO_SHORTEN_NAMES = True  # can be disabled to debug generated code if the names are hard to understand

SHORTEN_NAMES = {
    'radiation': 'rad',
    'time_step': 'step',
    'near_infrared': 'nir',
    'downwelling': 'down',
    'surface': 'sfc',
    'instantaneous': 'instant',
    'downward': 'down',
    'shortwave': 'sw',
    'longwave': 'lw',
    'coupling': 'cpl',
    'visible': 'vis',
    'ultraviolet': 'uv',
    'sensible_heat_flux': 'shf',
    'latent_heat_flux': 'lhf',
    'multiplied_by': 'times',
    'convective': 'conv',
    'precipitation': 'precip',
    'amount': 'amt',
    'accumulated': 'accum',
    'orographic': 'orog',
    'gravity': 'grav',
    'multiplication_factors': 'multiplic_facs',
    'specific_humidity': 'spec_hum',
    'at_lowest_model_layer': 'at_bottom',
    'updated_by_physics': 'after_physics',
    'multiplied_by_timestep': 'integrated',
    'cumulative': 'cumul',
    'for_coupling_multiplied_by_timestep': 'accum_for_cpl',
    'deep_convection': 'deepconv',
    'physics_timestep': 'phys_step',
    'water_vapor_specific_humidity': 'spec_hum',
    'perturbation': 'perturb',
    'tendency_of_air_temperature_due_to_radiative_heating': 'radiative_heating_rate',
    'tendency_of_air_temperature_due_to_longwave_heating': 'longwave_heating_rate',
    'tendency_of_air_temperature_due_to_shortwave_heating': 'shortwave_heating_rate',
    'cumulative_surface_net_downward_diffuse_ultraviolet_and_visible_shortwave_flux_for_coupling_multiplied_by_timestep': 'accum_sfc_dwn_diffuse_uv_vis_sw_flx_for_cpl',  # hard one to shorten
    'ozone': 'o3',
    'concentration': 'conc',
    'due_to': 'from',
    'production': 'produc',
    'maximum': 'max',
    'minimum': 'min',
    'reflectivity': 'reflec',
    'hourly': 'hrly',
    'cloud_liquid_water': 'cld_water',
    'fraction_of_grid_box': 'grid_frac',
    'higher_than': 'over',
    'critical_height': 'h_crit',
    'critical': 'crit',
    'grid_sensitive': 'grd_sensitv',
    'cloud': 'cld',
    'entrainment': 'entrnmnt',
    'instability': 'instab',
    'geopotential_difference_between_midlayers_divided_by_midlayer_virtual_temperature': 'gz_at_mid_over_virt_temperature_at_mid',
    'cloud_liquid_water': 'cld_water',
    'Monin_Obukhov': 'mon_obuk',
    'similarity': 'sim',
    'function': 'func',
    'momentum': 'mom',
    'dynamics_timestep': 'dyn_step',
    'nonnegative': 'nonneg',
    'over_ocean': 'ovr_ocn',
    'interface': 'iface',
    'between': 'btwn',
    'coefficient': 'coeff',
    'grid_size_related': 'grd_size',
    'scale_sensitive_schemes_complement': 'scl_sensitv_schem_compl',
    'type': 'typ',  # also need to replace reserved words
    'program': 'prgm',
    'real': 'rl',
    'stop': 'stap',  # confusing but I don't think this appears in any standard names anyways
    'end': 'nd',
    'dimensionless': 'unitless',
    'dimension': 'dim',
}


def shorten(standard_name):
    if DO_SHORTEN_NAMES:
        for long_name, short_name in _longest_keys_first(SHORTEN_NAMES.items()):
            standard_name = standard_name.replace(long_name, short_name)
    return standard_name


def _longest_keys_first(items):
    return sorted(items, key=lambda x: len(x[0]), reverse=True)


def get_module_list(scheme_list):
    module_dict = collections.defaultdict(list)
    for routine in meta.iterate_routines(scheme_list):
        module_name, extension = routine.filename.split('.')
        module_dict[module_name].append(routine.name)
    module_list = []
    for module_name, routine_list in module_dict.items():
        module_list.append({'name': module_name, 'members': routine_list})
    return module_list


def get_type_string(arg_type, arg_kind):
    if arg_type not in INTRINSIC_TYPES:
        arg_type = f"type({arg_type})"
    if arg_kind is None:
        return arg_type
    else:
        return f"{arg_type}({get_kind_string(arg_kind)})"


def fortran_dim_string(dimension):
    return shorten(dimension).replace('_plus_one', '+1')


def get_arg_list(args_in):
    arg_list = []
    for arg in args_in:
        arg_dict = {
            "type_string": get_type_string(arg.type, arg.kind),
            "intent": arg.intent,
            "name": shorten(arg.standard_name),
        }
        if len(arg.dimensions) > 0:
            arg_dict['dimensions'] = get_colon_dimension_string(arg.dimensions)  # f"({', '.join([fortran_dim_string(dim) for dim in arg.dimensions])})"
        else:
            arg_dict['dimensions'] = ''
        arg_list.append(arg_dict)
    return arg_list


def get_types(derived_data_types):
    return_list = []
    for ddt in derived_data_types:
        ddt_data = {}
        ddt_data['name'] = ddt.name
        ddt_data['packed_name'] = f"packed_{ddt.name.lower()}"
        attrs = []
        for attr in ddt.attrs:
            attr_data = {}
            attr_data['name'] = attr.name
            attr_data['standard_name'] = shorten(attr.standard_name)
            attr_data['is_subarray'] = '(' in attr.name
            attr_data['type'] = attr.type
            attr_data['type_string'] = get_type_string(attr.type, attr.kind)
            attr_data['dimensions'] = get_colon_dimension_string(attr.dimensions)
            attrs.append(attr_data)
        ddt_data['attrs'] = attrs
        ddt_data['attr_standard_names'] = [
            shorten(attr.standard_name) for attr in ddt.attrs
        ]
        return_list.append(ddt_data)
    return return_list


def get_kind_string(kind):
    if kind[:3] == 'len':
        return kind
    else:
        return 'kind=' + kind


def get_colon_dimension_string(dimensions):
    if len(dimensions) > 0:
        colon_list = [":" for d in dimensions]
        colon_string = ','.join(colon_list)
        return f"({colon_string})"
    else:
        return ""


def get_routines(schemes, derived_data_types):
    routine_list = []
    for routine in meta.iterate_routines(schemes):
        arg_list = get_arg_list(routine.args)
        do_errmsg = len(arg_list) > 0
        arg_list = arg_list[:-2]  # skip errmsg, errflg as these are added manually
        internal_arg_list = get_arg_list(routine.internal_args)
        internal_arg_list = internal_arg_list[:-2]
        routine_list.append(
            {
                'name': routine.name,
                'args': arg_list,
                'arg_names': [arg['name'] for arg in arg_list],
                'internal_arg_names': [arg['name'] for arg in arg_list],
                'derived_data_types': get_types(routine.types),
                'do_errmsg': do_errmsg,
            }
        )
    return routine_list


def get_modules(modules):
    return_list = []
    for module in modules:
        return_list.append({
            'name': module.name,
            'members': [member.name for member in module.members],

        })
    return return_list


if __name__ == '__main__':
    template_kwargs = {}
    ccpp_metadata = meta.load_meta_dir(FORTRAN_DIR)

    template_kwargs['derived_data_type_list'] = get_types(ccpp_metadata.types)
    template_kwargs['routine_list'] = get_routines(
        ccpp_metadata.schemes, ccpp_metadata.types)
    template_kwargs['module_list'] = get_modules(ccpp_metadata.modules)

    template_dir = os.path.join(LIB_DIR, 'templates')
    template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
    template_env = jinja2.Environment(loader=template_loader, autoescape=True, trim_blocks=True, lstrip_blocks=True)

    cap_template = template_env.get_template(CAP_BASENAME)
    result = cap_template.render(**template_kwargs)
    with open(CAP_OUT_FILENAME, 'w') as f:
        f.write(result)
