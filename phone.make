# -*-Makefile-*-

PYTHON=python
CWD:=$(shell pwd)

include compilers.make

ALL_PLATFORMS=arm

PLATFORMS=$(ALL_PLATFORMS)

PHONE_BRANCH_FILEIFIED=$(subst /,--,$(PHONE_BRANCH))

PHONE_LOCAL_BRANCH=$(PHONE_BRANCH_FILEIFIED)-gforge.phone

PYTHONPATH=lib/
export PYTHONPATH

OTHER_PLATFORMS=$(filter-out $(BUILD_PLATFORM), $(PLATFORMS))

INVOKE_GUP=$(PYTHON) gup-manager.py \
--platform $(1) \
--branch phone=$(PHONE_LOCAL_BRANCH)

INVOKE_GUB_BUILDER=$(PYTHON) gub-builder.py \
--target-platform $(1) \
--branch phone=$(PHONE_BRANCH):$(PHONE_LOCAL_BRANCH) \
$(foreach h,$(GUB_NATIVE_DISTCC_HOSTS), --native-distcc-host $(h))\
$(foreach h,$(GUB_CROSS_DISTCC_HOSTS), --cross-distcc-host $(h))\
$(LOCAL_GUB_BUILDER_OPTIONS)

INVOKE_INSTALLER_BUILDER=$(PYTHON) installer-builder.py \
  --target-platform $(1) \
  --branch phone=$(PHONE_LOCAL_BRANCH) \
  --version-db uploads/phone.db

BUILD=$(call INVOKE_GUB_BUILDER,$(1)) build $(2) \
  && $(call INVOKE_INSTALLER_BUILDER,$(1)) build-all phone

default: all

all: $(PLATFORMS)


download:
	$(foreach p, $(PLATFORMS), $(call INVOKE_GUB_BUILDER,$(p)) download phone && ) true

bootstrap: bootstrap-phone download-local local cross-compilers local-cross-tools download 

download-local:
	$(PYTHON) gub-builder.py $(LOCAL_GUB_BUILDER_OPTIONS) -p local download \
		phone pkg-config nsis icoutils 

local:
#	$(PYTHON) gub-builder.py $(LOCAL_GUB_BUILDER_OPTIONS) -p local build \
#		phone 

bootstrap-phone:

arm:
	$(call BUILD,$@,phone)

update-versions:
	python lib/versiondb.py --no-sources --url http://janneke/download --dbfile uploads/phone.db --download
