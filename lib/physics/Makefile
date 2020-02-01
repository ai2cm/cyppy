include ../conf/configure.fv3

LIBRARY  = libccpp.a
FFLAGS += -fPIC -cpp
CPPDEFS += -DCTYPES -DCCPP -DNEMS_GSM

SRCS_f = $(shell ls *.f)
SRCS_F = $(shell ls *.F)
SRCS_f90 = $(shell ls *.f90)
SRCS_F90 = $(shell ls *.F90)


DEPEND_FILES = $(SRCS_f) $(SRCS_f90) $(SRCS_F) $(SRCS_F90)

OBJS_f   = $(SRCS_f:.f=.o)
OBJS_f90 = $(SRCS_f90:.f90=.o)
OBJS_F   = $(SRCS_F:.F=.o)
OBJS_F90 = $(SRCS_F90:.F90=.o)
OBJS_c   = $(SRCS_c:.c=.o)

OBJS = $(OBJS_f) $(OBJS_f90) $(OBJS_F) $(OBJS_F90) $(OBJS_c)

all default: depend $(LIBRARY)

$(LIBRARY): $(OBJS)
	$(AR) $(ARFLAGS) $@ $?

.PHONY: clean
clean:
	@echo "Cleaning physics  ... "
	@echo
	$(RM) -f $(LIBRARY) *__genmod.f90 *.o */*.o *.mod *.i90 *.lst *.i depend */*.tmp.f90

MKDEPENDS = ../mkDepends.pl
include ../make.rules

include ./depend

# do not include 'depend' file if the target contains string 'clean'
ifneq (clean,$(findstring clean,$(MAKECMDGOALS)))
   -include depend
endif
