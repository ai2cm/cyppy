import os
import logging
import ctypes
import forge
import numpy as np
from . import meta


FILE_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(FILE_DIR, '../lib')
ERRLEN = 128

libccpp = ctypes.cdll.LoadLibrary(os.path.join(LIB_DIR, 'libccpp.so'))

CCPP_METADATA = meta.load_meta_dir(LIB_DIR)
STANDARD_NAME_TO_NAME = meta.get_standard_name_to_name(CCPP_METADATA)


class CCPPError(Exception):
    pass


def numpy_pointer(array):
    if array.dtype == np.float64:
        return array.ctypes.data_as(ctypes.POINTER(ctypes.c_double))
    elif array.dtype == np.float32:
        return array.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    elif array.dtype == np.bool:
        return array.ctypes.data_as(ctypes.POINTER(ctypes.c_bool))
    elif array.dtype == np.int32:
        return array.ctypes.data_as(ctypes.POINTER(ctypes.c_int))
    return ctypes.c_void_p(array.ctypes.data)


def get_python_routines(scheme):
    return_dict = {}
    for routine in scheme.init, scheme.run, scheme.finalize:
        return_dict[routine.name] = get_python_routine(routine)
    return return_dict


ERRMSG = ' ' * ERRLEN
ERRFLG = np.array(0)


def check_dimensions(array, signature, arg_dict):
    if len(array.shape) != len(signature.dimensions):
        raise CCPPError(
            f"value for {signature.name} should have dimensions "
            f"{signature.dimensions}, but it has {len(array.shape)} dimensions"
        )
    for length, dim_name in zip(array.shape, signature.dimensions):
        length_in_args = arg_dict[STANDARD_NAME_TO_NAME[dim_name]]
        if length != length_in_args:
            raise CCPPError(
                f"value for {signature.name} has a length of {length} for dimension "
                f"{dim_name}, but a value of {length_in_args} was given for {dim_name}"
            )


def check_type(array, signature):
    if signature.type == 'real' and not is_real(array.dtype):
        raise CCPPError(
            f"value for {signature.name} should be of type real, "
            f"but dtype {array.dtype} was given"
        )
    elif signature.type == 'integer' and not is_integer(array.dtype):
        raise CCPPError(
            f"value for {signature.name} should be of type integer, "
            f"but dtype {array.dtype} was given"
        )
    elif signature.type == 'logical' and not is_bool(array.dtype):
        raise CCPPError(
            f"value for {signature.name} should be of type logical, "
            f"but dtype {array.dtype} was given"
        )
    elif signature.type not in ('real', 'integer', 'logical'):
        raise NotImplementedError(f"Need code for type {signature.type}")


def is_real(dtype):
    return dtype in (np.float32, np.float64)


def is_integer(dtype):
    return dtype == np.int64


def is_bool(dtype):
    return dtype == np.bool


def get_python_routine(routine):
    f_routine = getattr(libccpp, f"{routine.name}_cap")
    @forge.sign(
        *[forge.pos(arg.name) for arg in routine.args[:-2]]  # skip errmsg, errflg args as we treat those internally
    )
    def python_routine(**kwargs):
        fortran_args = []
        logging.debug(f"calling routine {routine.name}")
        for signature in routine.args:
            if signature.name not in ('errmsg', 'errflg'):
                arg = kwargs[signature.name]
                if isinstance(arg, np.ndarray):
                    check_dimensions(arg, signature, kwargs)
                    check_type(arg, signature)
                    fortran_args.append(numpy_pointer(arg))
                else:
                    raise NotImplementedError()
        f_routine(*fortran_args, ERRMSG, numpy_pointer(ERRFLG))
        if ERRFLG != 0:
            raise CCPPError(f"{routine.name}: {ERRMSG}")
        logging.debug(f"completed routine {routine.name}")
    python_routine.__name__ = routine.name
    return python_routine


for scheme in CCPP_METADATA.schemes:
    locals().update(get_python_routines(scheme))
