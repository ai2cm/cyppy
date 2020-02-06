import os
import pytest
import tempfile
import os.path
import cyppy


TEST_DIR = os.path.dirname(os.path.realpath(__file__))
PHYSICS_F90_DIR = os.path.join(TEST_DIR, '../lib/test')


def get_meta_files(dirname):
    return [fname for fname in os.listdir(dirname) if fname.endswith('.meta')]


@pytest.fixture(params=get_meta_files(PHYSICS_F90_DIR))
def meta_filename(request):
    return os.path.join(PHYSICS_F90_DIR, request.param)


def test_load_meta_runs_without_error(meta_filename):
    cyppy.load_meta(meta_filename)


def assert_metadata_equal(result, target, filename=None):
    # don't check routine filenames because here we use tempfiles
    assert len(result.modules) == len(target.modules)
    for module_result, module_target in zip(result.modules, target.modules):
        if filename is not None:
            # module name is based on filename which will be corrupted by tempfile
            assert (
                module_result.name == os.path.basename(filename) or
                module_result.name == module_target.name)  # unless module specification provides it
        assert module_result.members == module_target.members
    assert len(result.schemes) == len(target.schemes)
    for scheme_result, scheme_target in zip(result.schemes, target.schemes):
        assert scheme_result.name == scheme_target.name
        for routine_type in ('init', 'run', 'finalize'):
            assert getattr(scheme_result, routine_type) == getattr(scheme_target, routine_type)
    assert result.types == target.types


@pytest.mark.parametrize(
    "meta_string, metadata",
    [
        pytest.param(
            """
[ccpp-arg-table]
  name = machine
  type = module
[kind_dyn]
  standard_name = kind_dyn
  long_name = definition of kind_dyn
  units = none
  dimensions = ()
  type = integer
[kind_grid]
  standard_name = kind_grid
  long_name = definition of kind_grid
  units = none
  dimensions = ()
  type = integer
""",
            cyppy.CCPPMetadata(
                modules=(cyppy.ModuleSpec(name="machine", members=("kind_dyn", "kind_grid")),),
                schemes=(),
                types=()
            ),
            id='module',
        ),
        pytest.param(
            """[ccpp-arg-table]
  name = cires_ugwp_run
  type = scheme
[me]
  standard_name = mpi_rank
  long_name = MPI rank of current process
  units = index
  dimensions = ()
  type = integer
  intent = in
  optional = F
[master]
  standard_name = mpi_root
  long_name = MPI rank of master process
  units = index
  dimensions = (vertical_dimension,horizontal_dimension)
  type = real
  kind = 8
  intent = in
  optional = T""",
            cyppy.CCPPMetadata(
                modules=(
                    cyppy.ModuleSpec(
                        name='cires_ugwp',
                        members=(
                            'cires_ugwp_finalize',
                            'cires_ugwp_init',
                            'cires_ugwp_run',
                        )
                    ),
                ),
                schemes=(
                    cyppy.SchemeSpec(
                        name='cires_ugwp',
                        init=cyppy.Routine(
                            name='cires_ugwp_init',
                            args=(),
                        ),
                        run=cyppy.Routine(
                            name='cires_ugwp_run',
                            args=(
                                cyppy.ArgSpec(
                                    name='me',
                                    standard_name='mpi_rank',
                                    long_name='MPI rank of current process',
                                    units='index',
                                    dimensions=(),
                                    type='integer',
                                    kind=None,
                                    intent='in',
                                    optional=False,
                                ),
                                cyppy.ArgSpec(
                                    name='master',
                                    standard_name='mpi_root',
                                    long_name='MPI rank of master process',
                                    units='index',
                                    dimensions=('vertical_dimension', 'horizontal_dimension'),
                                    type='real',
                                    kind='8',
                                    intent='in',
                                    optional=True,
                                ),
                            ),
                        ),
                        finalize=cyppy.Routine(
                            name='cires_ugwp_finalize',
                            args=(),
                        ),
                    ),
                ),
                types=(),
            ),
            id='run_only_scheme',
        ),
        pytest.param(
            """[ccpp-arg-table]
  name = cires_ugwp_run
  type = scheme
[me]
  standard_name = mpi_rank
  long_name = MPI rank of current process
  units = index
  dimensions = ()
  type = integer
  intent = in
  optional = F
[ccpp-arg-table]
  name = cires_ugwp_init
  type = scheme
[me]
  standard_name = mpi_rank
  long_name = MPI rank of current process
  units = index
  dimensions = ()
  type = integer
  intent = in
  optional = F""",
            cyppy.CCPPMetadata(
                modules=(
                    cyppy.ModuleSpec(
                        name='cires_ugwp',
                        members=(
                            'cires_ugwp_finalize',
                            'cires_ugwp_init',
                            'cires_ugwp_run',
                        )
                    ),
                ),
                schemes=(
                    cyppy.SchemeSpec(
                        name='cires_ugwp',
                        init=cyppy.Routine(
                            name='cires_ugwp_init',
                            args=(
                                cyppy.ArgSpec(
                                    name='me',
                                    standard_name='mpi_rank',
                                    long_name='MPI rank of current process',
                                    units='index',
                                    dimensions=(),
                                    type='integer',
                                    kind=None,
                                    intent='in',
                                    optional=False,
                                ),
                            ),
                        ),
                        run=cyppy.Routine(
                            name='cires_ugwp_run',
                            args=(
                                cyppy.ArgSpec(
                                    name='me',
                                    standard_name='mpi_rank',
                                    long_name='MPI rank of current process',
                                    units='index',
                                    dimensions=(),
                                    type='integer',
                                    kind=None,
                                    intent='in',
                                    optional=False,
                                ),
                            ),
                        ),
                        finalize=cyppy.Routine(
                            name='cires_ugwp_finalize',
                            args=(),
                        ),
                    ),
                ),
                types=()
            ),
            id="init_and_run_scheme",
        ),
        pytest.param(
            "",
            cyppy.CCPPMetadata(modules=(), schemes=(), types=()),
            id="empty_string",
        ),
        pytest.param(
            """[ccpp-arg-table]
  name = GFS_init_type
  type = ddt""",
            cyppy.CCPPMetadata(
                modules=(
                    cyppy.ModuleSpec(
                        name=None,
                        members=("GFS_init_type",),
                    ),
                ),
                schemes=(),
                types=(
                    cyppy.DerivedDataTypeSpec(
                        name="GFS_init_type",
                        attrs=()),
                )
            ),
            id="ddt_no_attrs",
        ),
        pytest.param(
            """[ccpp-arg-table]
  name = GFS_statein_type
  type = ddt
[phii]
  standard_name = geopotential_at_interface
  long_name = geopotential at model layer interfaces
  units = m2 s-2
  dimensions = (horizontal_dimension,vertical_dimension_plus_one)
  type = real
  kind = kind_phys""",
            cyppy.CCPPMetadata(
                modules=(
                    cyppy.ModuleSpec(
                        name=None,
                        members=("GFS_statein_type",),
                    ),
                ),
                schemes=(),
                types=(
                    cyppy.DerivedDataTypeSpec(
                        name="GFS_statein_type",
                        attrs=(
                            cyppy.AttributeSpec(
                                name='phii',
                                standard_name='geopotential_at_interface',
                                long_name='geopotential at model layer interfaces',
                                units='m2 s-2',
                                dimensions=(
                                    'horizontal_dimension',
                                    'vertical_dimension_plus_one'
                                ),
                                type='real',
                                kind='kind_phys',
                            ),
                        ),
                    ),
                ),
            ),
            id="ddt_one_attr",
        ),
    ]
)
def test_load_meta_equals(meta_string, metadata):
    with tempfile.NamedTemporaryFile(mode='w') as f:
        f.write(meta_string)
        f.flush()
        result = cyppy.load_meta(f.name)
    assert_metadata_equal(result, metadata, f.name)


@pytest.fixture
def arg_name():
    return 'arg'


@pytest.fixture
def base_arg_data():
    return {
        'standard_name': 'std_name',
        'long_name': 'long name',
        'dimensions': "()",
        'units': "units",
        'type': "type",
        'kind': "kind",
        'intent': "in",
        'optional': "T",
    }


@pytest.mark.parametrize(
    "dimensions_in, dimensions_out",
    [
        ("()", ()),
        ("(onlydim)", ('onlydim',)),
        ("(dim1,dim2)", ('dim1', 'dim2')),
        ("(dim1, dim2)", ('dim1', 'dim2'))
    ]
)
@pytest.mark.parametrize(
    'intent', ['in', 'out', 'inout']
)
@pytest.mark.parametrize(
    "optional_in, optional_out",
    [
        ('T', True),
        ('F', False),
    ]
)
def test_get_argument(
        arg_name, base_arg_data, dimensions_in, dimensions_out, intent,
        optional_in, optional_out):
    data = {}
    data.update(base_arg_data)
    data['dimensions'] = dimensions_in
    data['intent'] = intent
    data['optional'] = optional_in
    result = cyppy.meta.get_argument(arg_name, data)
    assert isinstance(result, cyppy.ArgSpec)
    for attr_name, attr_value in base_arg_data.items():
        if attr_name not in ('dimensions', 'intent', 'optional'):
            assert getattr(result, attr_name) == attr_value
    assert result.dimensions == dimensions_out
    assert result.intent == intent
    assert result.optional == optional_out


@pytest.mark.parametrize(
    "invalid_data",
    [
        {'optional': 'sometimes'},
        {'intent': 'returned'},
        {'dimensions': 'dim1, dim2'},
        {'dimensions': 'dim1'},
    ]
)
def test_get_argument_invalid(
        arg_name, base_arg_data, invalid_data):
    data = {}
    data.update(base_arg_data)
    data.update(invalid_data)
    with pytest.raises(ValueError):
        cyppy.meta.get_argument(arg_name, data)


@pytest.fixture
def attribute_name():
    return 'attribute'


@pytest.fixture
def base_attribute_data():
    return {
        'standard_name': 'std_name',
        'long_name': 'long name',
        'dimensions': "()",
        'units': "units",
        'type': "type",
        'kind': "kind",
    }


@pytest.mark.parametrize(
    "dimensions_in, dimensions_out",
    [
        ("()", ()),
        ("(onlydim)", ('onlydim',)),
        ("(dim1,dim2)", ('dim1', 'dim2')),
        ("(dim1, dim2)", ('dim1', 'dim2'))
    ]
)
def test_get_attribute(
        attribute_name, base_attribute_data, dimensions_in, dimensions_out):
    data = {}
    data.update(base_attribute_data)
    data['dimensions'] = dimensions_in
    result = cyppy.meta.get_attribute(attribute_name, data)
    assert isinstance(result, cyppy.AttributeSpec)
    for attr_name, attr_value in base_attribute_data.items():
        if attr_name != 'dimensions':
            assert getattr(result, attr_name) == attr_value
    assert result.dimensions == dimensions_out


@pytest.mark.parametrize(
    "invalid_data",
    [
        {'dimensions': 'dim1, dim2'},
        {'dimensions': 'dim1'},
    ]
)
def test_get_attribute_invalid(
        attribute_name, base_attribute_data, invalid_data):
    data = {}
    data.update(base_attribute_data)
    data.update(invalid_data)
    with pytest.raises(ValueError):
        cyppy.meta.get_attribute(attribute_name, data)


@pytest.mark.parametrize(
    "dimensions_in, dimensions_out",
    [
        pytest.param(
            "()",
            (),
            id="empty",
        ),
        pytest.param(
            "(arg1)",
            ("arg1",),
            id="1D",
        ),
        pytest.param(
            "(dim1,dim2,dim3)",
            ("dim1", "dim2", "dim3"),
            id="3D",
        ),
        pytest.param(
            "(dim1, dim2)",
            ("dim1", "dim2"),
            id="2D with space",
        )
    ]
)
def test_get_dimensions(dimensions_in, dimensions_out):
    result = cyppy.meta.get_dimensions(dimensions_in)
    assert result == dimensions_out


@pytest.mark.parametrize(
    "modules_in, modules_out",
    [
        pytest.param([], [], id="no_modules"),
        pytest.param(
            [cyppy.ModuleSpec(name='module', members=())],
            [],
            id="one_empty_module"
        ),
        pytest.param(
            [cyppy.ModuleSpec(name='module', members=('member1',))],
            [cyppy.ModuleSpec(name='module', members=('member1',))],
            id="one_valid_module"
        ),
        pytest.param(
            [cyppy.ModuleSpec(name='module1', members=('member1',)),
             cyppy.ModuleSpec(name='module2', members=('member2',))],
            [cyppy.ModuleSpec(name='module1', members=('member1',)),
             cyppy.ModuleSpec(name='module2', members=('member2',))],
            id="two_different_modules"
        ),
        pytest.param(
            [cyppy.ModuleSpec(name='module1', members=('member1', 'member3')),
             cyppy.ModuleSpec(name='module2', members=('member2', 'member4'))],
            [cyppy.ModuleSpec(name='module1', members=('member1', 'member3')),
             cyppy.ModuleSpec(name='module2', members=('member2', 'member4'))],
            id="two_longer_different_modules"
        ),
        pytest.param(
            [cyppy.ModuleSpec(name='module1', members=('member1', 'member3')),
             cyppy.ModuleSpec(name='module1', members=('member2', 'member4'))],
            [cyppy.ModuleSpec(
                name='module1',
                members=('member1', 'member2', 'member3', 'member4')
            )],
            id="two_longer_same_module"
        ),
    ]
)
def test_consolidate_modules(modules_in, modules_out):
    result = cyppy.meta.consolidate_modules(modules_in)
    assert result == modules_out


@pytest.mark.parametrize(
    "invalid_module",
    [
        cyppy.ModuleSpec(name='module1', members='member'),
    ]
)
def test_consolidate_modules_invalid_module(invalid_module):
    with pytest.raises(ValueError):
        cyppy.meta.consolidate_modules([invalid_module])


@pytest.fixture
def not_ddt_arg():
    return cyppy.ArgSpec(
        name='me',
        standard_name='mpi_rank',
        long_name='MPI rank of current process',
        units='index',
        dimensions=(),
        type='integer',
        kind=None,
        intent='in',
        optional=False,
    )


@pytest.fixture
def ddt_arg():
    return cyppy.ArgSpec(
        name='der',
        standard_name='derived_value',
        long_name='MPI rank of current process',
        units='index',
        dimensions=(),
        type='My_Type',
        kind=None,
        intent='in',
        optional=False,
    )


@pytest.fixture
def ddt():
    return cyppy.DerivedDataTypeSpec(
        name='My_Type',
        attrs=(
            cyppy.AttributeSpec(
                name='phii',
                standard_name='geopotential_at_interface',
                long_name='geopotential at model layer interfaces',
                units='m2 s-2',
                dimensions=(
                    'horizontal_dimension',
                    'vertical_dimension_plus_one'
                ),
                type='real',
                kind='kind_phys',
            ),
        )
    )


@pytest.fixture
def ddt_args_out(ddt, ddt_arg):
    args_out = []
    for attr in ddt.attrs:
        args_out.append(
            cyppy.meta.get_argument_from_attribute(
                attr, ddt_arg.intent, ddt_arg.optional)
        )
    return tuple(args_out)


def test_expand_derived_args_no_ddt(not_ddt_arg):
    ddt_lookup = {}
    ddt_used = []
    args_in = (not_ddt_arg,)
    args_out = cyppy.meta.expand_derived_args(args_in, ddt_lookup, ddt_used)
    assert tuple(args_out) == args_in


def test_expand_derived_args_with_ddt(ddt_arg, ddt, ddt_args_out):
    ddt_lookup = {ddt.name: ddt}
    ddt_used = []
    args_in = (ddt_arg,)
    args_out = cyppy.meta.expand_derived_args(args_in, ddt_lookup, ddt_used)
    assert tuple(args_out) == ddt_args_out
    assert ddt_used == [ddt]


def test_expand_derived_args_empty():
    result = cyppy.meta.expand_derived_args([], {}, [])
    assert result == []


if __name__ == '__main__':
    pytest.main()
