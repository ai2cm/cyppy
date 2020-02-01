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

COPY cyppy $CYPPY_DIR
COPY lib $LIB_DIR
COPY tests $CYPPY_DIR/tests
COPY setup.py README.rst HISTORY.rst requirements.txt $CYPPY_DIR/

RUN pip install -r $CYPPY_DIR/requirements.txt

ARG compile_option
ARG configure_file=configure.fv3.gnu_docker

# copy appropriate configuration file to configure.fv3
RUN cp $LIB_DIR/conf/$configure_file \
        $LIB_DIR/conf/configure.fv3 && \
    if [ ! -z $compile_option ]; then sed -i "33i $compile_option" \
        $LIB_DIR/conf/configure.fv3; fi

RUN cd $LIB_DIR && make

CMD ["bash", "pip install -e /cyppy"]
