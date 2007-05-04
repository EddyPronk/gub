CWD:=$(shell pwd)
PYTHON=python
#PYTHONPATH=gub
#export PYTHONPATH

## must always have one host.
GUB_DISTCC_ALLOW_HOSTS=127.0.0.1

GUB_BUILDER = $(PYTHON) bin/gub
GUP_MANAGER = $(PYTHON) bin/gpkg
INSTALLER_BUILDER = $(PYTHON) bin/installer-builder
CYGWIN_PACKAGER = $(PYTHON) bin/cygwin-packager

INVOKE_GUB_BUILDER=$(GUB_BUILDER)\
 --target-platform $(1)\
 $(GUB_ONLINE_OPTION) \
 $(foreach h,$(GUB_NATIVE_DISTCC_HOSTS), --native-distcc-host $(h))\
 $(foreach h,$(GUB_CROSS_DISTCC_HOSTS), --cross-distcc-host $(h))\
 $(GUB_BUILDER_OPTIONS)\
 $(LOCAL_GUB_BUILDER_OPTIONS)


INVOKE_GUP=$(GUP_MANAGER)\
 --platform $(1)\
 $(GUP_OPTIONS)

INVOKE_INSTALLER_BUILDER=$(INSTALLER_BUILDER)\
 --target-platform $(1)\
 $(INSTALLER_BUILDER_OPTIONS)

BUILD=$(call INVOKE_GUB_BUILDER,$(1)) $(2)\
  && $(call INVOKE_INSTALLER_BUILDER,$(1)) build-all $(PACKAGE)

BUILD_PLATFORM = $(shell $(PYTHON) bin/build-platform)
OTHER_PLATFORMS=$(filter-out $(BUILD_PLATFORM), $(PLATFORMS))
