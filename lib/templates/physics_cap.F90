module physics_cap_mod

use iso_c_binding

{% for module in module_list %}
use {{ module.name }}, only: {{ module.members|join(', ') }}
{% endfor %}
use machine, only: kind_phys

implicit none
public h2ophys_init
public

integer, parameter :: errlen = 128

contains

{% for routine in routine_list %}
    {% if routine.arg_names %}
    subroutine {{ routine.name }}_cap({{ routine.arg_names|join(', &\n')|safe }}, errmsg, errflg) bind(c)
    {% else %}
    subroutine {{ routine.name }}_cap(errmsg, errflg) bind(c)
    {% endif %}
    {% for arg in routine.args %}
        {{ arg.type }}, intent({{ arg.intent }}) :: {{ arg.name }}{{ arg.dimensions }}
    {% endfor %}
        character(kind=c_char), dimension(errlen), intent(out) :: errmsg
        integer,                                   intent(out) :: errflg
        character(kind=c_char, len=errlen) :: errmsg_fortran
        integer                            :: i
        print *, "ENTER {{ routine.name }}"
    {% if routine.arg_names %}
        call {{ routine.name }}({{ routine.arg_names|join(', &\n')|safe }}, errmsg_fortran, errflg)
    {% else %}
        call {{ routine.name }}()
    {% endif %}
        errmsg_fortran = trim(errmsg_fortran) // c_null_char
        do i = 1, errlen
            errmsg(i) = errmsg_fortran(i:i)
        enddo
        print *, "EXIT {{ routine.name }}"
        end subroutine {{ routine.name }}_cap
{% endfor %}

end module physics_cap_mod
