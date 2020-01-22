GCR_URL = us.gcr.io/vcm-ml
COMPILED_TAG_NAME ?= default
COMPILE_OPTION ?=

COMPILED_IMAGE ?= $(GCR_URL)/ccpp
ENVIRONMENT_IMAGE=$(GCR_URL)/ccpp-environment
IMAGE ?= $(ENVIRONMENT_IMAGE)

MOUNTS= -v $(shell pwd):/ccpp

EXPERIMENT ?= new
RUNDIR_CONTAINER=/FV3/rundir
RUNDIR_HOST=$(shell pwd)/experiments/$(EXPERIMENT)/rundir

build: build_compiled

build_environment:
	docker build -f Dockerfile -t $(ENVIRONMENT_IMAGE) --target ccpp-environment .

build_compiled: build_environment
	docker build \
		-f Dockerfile \
		-t $(COMPILED_IMAGE) \
		--target ccpp .

enter: build_environment
	docker run --rm $(MOUNTS) -w /ccpp -it $(IMAGE) bash

.PHONY: build build_environment build_compiled enter run test test_32bit
