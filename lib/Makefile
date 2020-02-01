include ./conf/configure.fv3
SHELL = /bin/sh

CAP_SRC = physics_cap.F90
SHARED_LIBRARY = libccpp.so
CCPP_DIR = ./physics
CCPP_SRC = $(shell ls $(CCPP_DIR)/*.F90 $(CCPP_DIR)/*.f90 $(CCPP_DIR)/*.f $(CCPP_DIR)/*.F)
CCPP_META = $(shell ls $(CCPP_DIR)/*.meta)
CCPP_LIBRARY  = libccpp.a

FFLAGS += -fPIC -cpp -I./physics
CPPDEFS += -DCTYPES -DCCPP


all: $(SHARED_LIBRARY)

$(CAP_SRC): templates/$(CAP_SRC) $(CCPP_SRC) make_cap.py $(CCPP_META)
	python3 make_cap.py

$(CCPP_DIR)/$(CCPP_LIBRARY): $(CCPP_SRC)
	cd $(CCPP_DIR) && make

$(SHARED_LIBRARY): $(CAP_SRC) $(CCPP_DIR)/$(CCPP_LIBRARY)
	$(FC) -shared $(FFLAGS) -o $@ $^

clean:
	@echo "Cleaning ... "
	$(RM) -f *.o *.mod *.lst depend $(SHARED_LIBRARY) $(CAP_SRC)
	$(MAKE) -C $(FV3GFS_BUILD_DIR) clean

cleanall: clean

.PHONY: clean cleanall
