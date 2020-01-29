module physics_cap_mod

use iso_c_binding


use h2ophys, only: h2ophys_init, h2ophys_run, h2ophys_finalize

use sfc_ocean, only: sfc_ocean_init, sfc_ocean_run, sfc_ocean_finalize

use machine, only: kind_phys

implicit none
public h2ophys_init
public

integer, parameter :: errlen = 128

contains


    
    subroutine h2ophys_init_cap(errmsg, errflg) bind(c)
    
    
        character(kind=c_char), dimension(errlen), intent(out) :: errmsg
        integer,                                   intent(out) :: errflg
        character(kind=c_char, len=errlen) :: errmsg_fortran
        integer                            :: i
        print *, "ENTER h2ophys_init"
    
        call h2ophys_init()
    
        errmsg_fortran = trim(errmsg_fortran) // c_null_char
        do i = 1, errlen
            errmsg(i) = errmsg_fortran(i:i)
        enddo
        print *, "EXIT h2ophys_init"
        end subroutine h2ophys_init_cap

    
    subroutine h2ophys_run_cap(ix, &
im, &
levs, &
kh2o, &
dt, &
h2o, &
ph2o, &
prsl, &
h2opltc, &
h2o_coeff, &
ldiag3d, &
me, errmsg, errflg) bind(c)
    
    
        integer, intent(in) :: ix
    
        integer, intent(in) :: im
    
        integer, intent(in) :: levs
    
        integer, intent(in) :: kh2o
    
        real(kind=kind_phys), intent(in) :: dt
    
        real(kind=kind_phys), intent(inout) :: h2o(ix, levs)
    
        real(kind=kind_phys), intent(in) :: ph2o(kh2o)
    
        real(kind=kind_phys), intent(in) :: prsl(ix, levs)
    
        real(kind=kind_phys), intent(in) :: h2opltc(ix, kh2o, h2o_coeff)
    
        integer, intent(in) :: h2o_coeff
    
        logical, intent(in) :: ldiag3d
    
        integer, intent(in) :: me
    
        character(kind=c_char), dimension(errlen), intent(out) :: errmsg
        integer,                                   intent(out) :: errflg
        character(kind=c_char, len=errlen) :: errmsg_fortran
        integer                            :: i
        print *, "ENTER h2ophys_run"
    
        call h2ophys_run(ix, &
im, &
levs, &
kh2o, &
dt, &
h2o, &
ph2o, &
prsl, &
h2opltc, &
h2o_coeff, &
ldiag3d, &
me, errmsg_fortran, errflg)
    
        errmsg_fortran = trim(errmsg_fortran) // c_null_char
        do i = 1, errlen
            errmsg(i) = errmsg_fortran(i:i)
        enddo
        print *, "EXIT h2ophys_run"
        end subroutine h2ophys_run_cap

    
    subroutine h2ophys_finalize_cap(errmsg, errflg) bind(c)
    
    
        character(kind=c_char), dimension(errlen), intent(out) :: errmsg
        integer,                                   intent(out) :: errflg
        character(kind=c_char, len=errlen) :: errmsg_fortran
        integer                            :: i
        print *, "ENTER h2ophys_finalize"
    
        call h2ophys_finalize()
    
        errmsg_fortran = trim(errmsg_fortran) // c_null_char
        do i = 1, errlen
            errmsg(i) = errmsg_fortran(i:i)
        enddo
        print *, "EXIT h2ophys_finalize"
        end subroutine h2ophys_finalize_cap

    
    subroutine sfc_ocean_init_cap(errmsg, errflg) bind(c)
    
    
        character(kind=c_char), dimension(errlen), intent(out) :: errmsg
        integer,                                   intent(out) :: errflg
        character(kind=c_char, len=errlen) :: errmsg_fortran
        integer                            :: i
        print *, "ENTER sfc_ocean_init"
    
        call sfc_ocean_init()
    
        errmsg_fortran = trim(errmsg_fortran) // c_null_char
        do i = 1, errlen
            errmsg(i) = errmsg_fortran(i:i)
        enddo
        print *, "EXIT sfc_ocean_init"
        end subroutine sfc_ocean_init_cap

    
    subroutine sfc_ocean_run_cap(im, &
cp, &
rd, &
eps, &
epsm1, &
hvap, &
rvrdm1, &
ps, &
t1, &
q1, &
tskin, &
cm, &
ch, &
prsl1, &
prslki, &
wet, &
wind, &
flag_iter, &
qsurf, &
cmm, &
chh, &
gflux, &
evap, &
hflx, &
ep, errmsg, errflg) bind(c)
    
    
        integer, intent(in) :: im
    
        real(kind=kind_phys), intent(in) :: cp
    
        real(kind=kind_phys), intent(in) :: rd
    
        real(kind=kind_phys), intent(in) :: eps
    
        real(kind=kind_phys), intent(in) :: epsm1
    
        real(kind=kind_phys), intent(in) :: hvap
    
        real(kind=kind_phys), intent(in) :: rvrdm1
    
        real(kind=kind_phys), intent(in) :: ps(im)
    
        real(kind=kind_phys), intent(in) :: t1(im)
    
        real(kind=kind_phys), intent(in) :: q1(im)
    
        real(kind=kind_phys), intent(in) :: tskin(im)
    
        real(kind=kind_phys), intent(in) :: cm(im)
    
        real(kind=kind_phys), intent(in) :: ch(im)
    
        real(kind=kind_phys), intent(in) :: prsl1(im)
    
        real(kind=kind_phys), intent(in) :: prslki(im)
    
        logical, intent(in) :: wet(im)
    
        real(kind=kind_phys), intent(in) :: wind(im)
    
        logical, intent(in) :: flag_iter(im)
    
        real(kind=kind_phys), intent(inout) :: qsurf(im)
    
        real(kind=kind_phys), intent(inout) :: cmm(im)
    
        real(kind=kind_phys), intent(inout) :: chh(im)
    
        real(kind=kind_phys), intent(inout) :: gflux(im)
    
        real(kind=kind_phys), intent(inout) :: evap(im)
    
        real(kind=kind_phys), intent(inout) :: hflx(im)
    
        real(kind=kind_phys), intent(inout) :: ep(im)
    
        character(kind=c_char), dimension(errlen), intent(out) :: errmsg
        integer,                                   intent(out) :: errflg
        character(kind=c_char, len=errlen) :: errmsg_fortran
        integer                            :: i
        print *, "ENTER sfc_ocean_run"
    
        call sfc_ocean_run(im, &
cp, &
rd, &
eps, &
epsm1, &
hvap, &
rvrdm1, &
ps, &
t1, &
q1, &
tskin, &
cm, &
ch, &
prsl1, &
prslki, &
wet, &
wind, &
flag_iter, &
qsurf, &
cmm, &
chh, &
gflux, &
evap, &
hflx, &
ep, errmsg_fortran, errflg)
    
        ! errmsg_fortran = trim(errmsg_fortran) // c_null_char
        ! do i = 1, errlen
        !     errmsg(i) = errmsg_fortran(i:i)
        ! enddo
        print *, "EXIT sfc_ocean_run"
        end subroutine sfc_ocean_run_cap

    
    subroutine sfc_ocean_finalize_cap(errmsg, errflg) bind(c)
    
    
        character(kind=c_char), dimension(errlen), intent(out) :: errmsg
        integer,                                   intent(out) :: errflg
        character(kind=c_char, len=errlen) :: errmsg_fortran
        integer                            :: i
        print *, "ENTER sfc_ocean_finalize"
    
        call sfc_ocean_finalize()
    
        errmsg_fortran = trim(errmsg_fortran) // c_null_char
        do i = 1, errlen
            errmsg(i) = errmsg_fortran(i:i)
        enddo
        print *, "EXIT sfc_ocean_finalize"
        end subroutine sfc_ocean_finalize_cap


end module physics_cap_mod