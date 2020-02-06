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

## Build CCPP
##---------------------------------------------------------------------------------
FROM ccpp-environment AS ccpp

RUN apt-get update && apt-get install -y \
    nano \
    python3 \
    python3-pip && \
    ln -s /bin/python3 /bin/python && \
    ln -s /bin/pip3 /bin/pip

ARG CYPPY_DIR=/cyppy
ARG LIB_DIR=$CYPPY_DIR/lib

COPY requirements.txt $CYPPY_DIR/
RUN pip install -r $CYPPY_DIR/requirements.txt

COPY cyppy $CYPPY_DIR/cyppy
COPY lib $LIB_DIR
COPY tests $CYPPY_DIR/tests
COPY setup.py README.rst HISTORY.rst $CYPPY_DIR/

ARG compile_option
ARG configure_file=configure.fv3.gnu_docker

# copy appropriate configuration file to configure.fv3
RUN cp $LIB_DIR/conf/$configure_file \
        $LIB_DIR/conf/configure.fv3 && \
    if [ ! -z $compile_option ]; then sed -i "33i $compile_option" \
        $LIB_DIR/conf/configure.fv3; fi

RUN pip install -e /cyppy

# RUN cd $LIB_DIR && make clean && make

CMD ["bash"]
