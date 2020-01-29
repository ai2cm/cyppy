

CAP_SRC = physics_cap.F90
LIBRARY  = libccpp.a
SHARED_LIBRARY = libccpp.so
FFLAGS += -fPIC -g

SRCS_f = h2ophys.f
SRCS_F = machine.F sfc_ocean.F
SRCS_f90 = funcphys.f90
SRCS_F90 = physcons.F90


DEPEND_FILES = $(SRCS_f) $(SRCS_f90) $(SRCS_F) $(SRCS_F90)

OBJS_f   = $(SRCS_f:.f=.o)
OBJS_f90 = $(SRCS_f90:.f90=.o)
OBJS_F   = $(SRCS_F:.F=.o)
OBJS_F90 = $(SRCS_F90:.F90=.o)
OBJS_c   = $(SRCS_c:.c=.o)

OBJS = $(OBJS_f) $(OBJS_f90) $(OBJS_F) $(OBJS_F90) $(OBJS_c)

all default: depend $(SHARED_LIBRARY)

$(LIBRARY): $(OBJS)
	$(AR) $(ARFLAGS) $@ $?

$(SHARED_LIBRARY): $(CAP_SRC) $(LIBRARY)
	$(FC) -shared $(FFLAGS) -o $@ $^

.PHONY: clean
clean:
	@echo "Cleaning gfsphysics  ... "
	@echo
	$(RM) -f $(LIBRARY) *__genmod.f90 *.o */*.o *.mod *.i90 *.lst *.i depend */*.tmp.f90

MKDEPENDS = ../mkDepends.pl
include ../make.rules

include ./depend

# do not include 'depend' file if the target contains string 'clean'
ifneq (clean,$(findstring clean,$(MAKECMDGOALS)))
   -include depend
endif
