FROM ubuntu:19.10 AS ccpp-environment

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gcc \
    git \
    libblas-dev \
    liblapack-dev \
    libnetcdf-dev \
    libnetcdff-dev \
    perl \
    make \
    cmake \
    rsync \
    libffi-dev \
    openssl \
    libopenmpi3 \
    bats

# download and install NCEP libraries
RUN git config --global http.sslverify false && \
    git clone https://github.com/NCAR/NCEPlibs.git && \
    mkdir /opt/NCEPlibs && \
    cd NCEPlibs && \
    git checkout 3da51e139d5cd731c9fc27f39d88cb4e1328212b && \
    echo "y" | ./make_ncep_libs.sh -s linux -c gnu -d /opt/NCEPlibs -o 1

## Build FMS
##---------------------------------------------------------------------------------
FROM ccpp-environment AS fms-build

ENV FMS_DIR=/FMS
ENV CC=mpicc
ENV FC=mpifort
ENV LDFLAGS="-L/usr/lib"
ENV LOG_DRIVER_FLAGS="--comments"
ENV CPPFLAGS="-I/usr/include -Duse_LARGEFILE -DMAXFIELDMETHODS_=500"
ENV FCFLAGS="-fcray-pointer -Waliasing -ffree-line-length-none -fno-range-check -fdefault-real-8 -fdefault-double-8 -fopenmp"

# this PR contains fixes we need to build in docker, can update to master repo when merged
RUN git clone -b better.apple.support --depth 1 https://github.com/underwoo/FMS.git $FMS_DIR
RUN cd $FMS_DIR && autoreconf --install && ./configure
RUN cd $FMS_DIR && make -j8
RUN ln -s $FMS_DIR/*/*.mod $FMS_DIR/*/*.o $FMS_DIR/*/*.h $FMS_DIR/

## Build ESMF
##---------------------------------------------------------------------------------
FROM ccpp-environment as esmf-build

ENV ESMF_DIR=/esmf
ENV ESMF_INSTALL_PREFIX=/usr/local/esmf
ENV ESMF_NETCDF_INCLUDE=/usr/include
ENV ESMF_NETCDF_LIBS="-lnetcdf -lnetcdff"
ENV ESMF_BOPT=O3

RUN git clone -b ESMF_8_0_0 --depth 1 https://git.code.sf.net/p/esmf/esmf $ESMF_DIR
RUN cd $ESMF_DIR && make lib -j8 && make install && make installcheck

## Build FV3 executable in its own image
##---------------------------------------------------------------------------------
FROM ccpp-environment AS ccpp

RUN apt-get update && apt-get install -y \
    nano \
    python3 \
    python3-pip && \
    ln -s /bin/python3 /bin/python && \
    ln -s /bin/pip3 /bin/pip

ENV FMS_DIR=/FMS
ENV ESMF_DIR=/usr/local/esmf
ENV ESMF_INC="-I/usr/local/esmf/include -I${ESMF_DIR}/mod/modO3/Linux.gfortran.64.mpiuni.default/"
ENV LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${ESMF_DIR}/lib/libO3/Linux.gfortran.64.mpiuni.default/:${FMS_DIR}/libFMS/.libs/

COPY --from=fv3gfs-fms /FMS $FMS_DIR
COPY --from=fv3gfs-esmf /usr/local/esmf ${ESMF_DIR}
COPY cyppy /cyppy
COPY lib /cyppy/lib
COPY tests /cyppy/tests
COPY setup.py README.rst HISTORY.rst requirements.txt /cyppy/

RUN pip install -r /cyppy/requirements.txt

#ARG compile_option
#ARG configure_file=configure.fv3.gnu_docker

# copy appropriate configuration file to configure.fv3
#RUN cp /FV3/conf/$configure_file \
#        /FV3/conf/configure.fv3 && \
#    if [ ! -z $compile_option ]; then sed -i "33i $compile_option" \
#        /FV3/conf/configure.fv3; fi

CMD ["bash", "pip install -e /cyppy"]
