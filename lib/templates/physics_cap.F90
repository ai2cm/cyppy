module physics_cap_mod

use iso_c_binding

{% for module in module_list %}
use {{ module.name }}, only: &
    {{ module.members|join(', &\n    ')|safe }}

{% endfor %}

use machine, only: kind_phys

implicit none

public

integer, parameter :: errlen = 128

contains

{% for ddt in derived_data_type_list %}
    subroutine pack_{{ ddt.name }}( &
    {% if ddt.attrs %}
    &   {{ ddt.attr_standard_names|join(', &\n    &   ')|safe }}, &
    {% endif %}
    &   ddt_out)
    {% for attr in ddt.attrs %}
        {{ attr.type_string }}, TARGET, intent(in) :: {{ attr.standard_name }}{{ attr.dimensions }}
    {% endfor %}
        type({{ ddt.name }}), intent(out) :: ddt_out

    {% for attr in ddt.attrs %}
        {% if attr.is_subarray or (attr.dimensions|length == 0) %}
        ddt_out%{{ attr.name }} = {{ attr.standard_name }}
        {% else %}
        ddt_out%{{ attr.name }} => {{ attr.standard_name }}
        {% endif %}
    {% endfor %}
    end subroutine pack_{{ ddt.name }}

    subroutine unpack_{{ ddt.name }}( &
    &   ddt_in{% if ddt.attrs %}, &
    &   {{ ddt.attr_standard_names|join(', &\n    &   ')|safe }}{% endif %})
        type({{ ddt.name }}), intent(in) :: ddt_in
    {% for attr in ddt.attrs %}
        {{ attr.type_string }}, intent(inout) :: {{ attr.standard_name }}{{ attr.dimensions }}
    {% endfor %}

    {% for attr in ddt.attrs %}
        {% if attr.is_subarray or (attr.dimensions|length == 0) %}
        {{ attr.standard_name }} = ddt_in%{{ attr.name }}
        {% endif %}
    {% endfor %}
    end subroutine unpack_{{ ddt.name }}

{% endfor %}
{% for routine in routine_list %}
    {% if routine.arg_names %}
    subroutine {{ routine.name }}_cap( &
        {{ routine.arg_names|join(', &\n        ')|safe }}, errmsg, errflg) bind(c)
    {% else %}
    subroutine {{ routine.name }}_cap(errmsg, errflg) bind(c)
    {% endif %}
    {% for arg in routine.args %}
        {{ arg.type_string }}, intent({{ arg.intent }}) :: {{ arg.name }}{{ arg.dimensions }}
    {% endfor %}
    {% for ddt in routine.derived_data_types %}
        {{ ddt.name }} :: {{ ddt.packed_name }}
    {% endfor %}
        character(kind=c_char), dimension(errlen), intent(out) :: errmsg
        integer,                                   intent(out) :: errflg
        character(kind=c_char, len=errlen) :: errmsg_fortran
        integer                            :: i

        print *, "ENTER {{ routine.name }}"

    {% for ddt in routine.derived_data_types %}
        call pack_{{ ddt.name }}( &
            {{ ddt.attr_standard_names|join(', &\n            ')|safe }}, &
            {{ ddt.packed_name }})

    {% endfor %}
    {% if routine.do_errmsg %}
        call {{ routine.name }}( &
        {% if routine.internal_arg_names %}
            {{ routine.internal_arg_names|join(', &\n            ')|safe }}, &
        {% endif %}
            errmsg_fortran, &
            errflg)

    {% else %}
        call {{ routine.name }}()

    {% endif %}
    {% for ddt in routine.derived_data_types %}
        call unpack_{{ ddt.name }}( &
            {{ ddt.packed_name }}, &
            {{ ddt.attr_standard_names|join(', &\n            ')|safe }})

    {% endfor %}
    {% if routine.do_errmsg %}
        errmsg_fortran = trim(errmsg_fortran) // c_null_char
        do i = 1, errlen
            errmsg(i) = errmsg_fortran(i:i)
        enddo

    {% endif %}
        print *, "EXIT {{ routine.name }}"

    end subroutine {{ routine.name }}_cap

{% endfor %}

end module physics_cap_mod
