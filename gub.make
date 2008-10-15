CWD:=$(shell pwd)
PYTHON=python
PYTHONPATH=.
export PYTHONPATH

-include local.make

## must always have one host.
GUB_DISTCC_ALLOW_HOSTS=127.0.0.1

GUB = $(PYTHON) bin/gub
GPKG = $(PYTHON) bin/gpkg
INSTALLER_BUILDER = $(PYTHON) bin/installer-builder
CYGWIN_PACKAGER = $(PYTHON) bin/cygwin-packager \
 $(CYGWIN_PACKAGER_OPTIONS)\
 $(LOCAL_CYGWIN_PACKAGER_OPTIONS)

ifneq ($(LOCAL_GUB_BUILDER_OPTIONS),)
$(warning LOCAL_GUB_BUILDER_OPTIONS is deprecated, use LOCAL_GUB_OPTIONS)
LOCAL_GUB_OPTIONS += $(LOCAL_GUB_BUILDER_OPTIONS)
endif

LOCAL_GUB_OPTIONS += $(GUB_ONLINE_OPTION)

INVOKE_GUB=$(GUB)\
 --platform=$(1)\
$(foreach h,$(GUB_NATIVE_DISTCC_HOSTS), --native-distcc-host=$(h))\
$(foreach h,$(GUB_CROSS_DISTCC_HOSTS), --cross-distcc-host=$(h))\
 $(GUB_OPTIONS)\
 $(LOCAL_GUB_OPTIONS)

INVOKE_GUP=$(GPKG)\
 --platform=$(1)\
 $(GPKG_OPTIONS)\
 $(LOCAL_GPKG_OPIONS)

INVOKE_INSTALLER_BUILDER=$(INSTALLER_BUILDER)\
 --platform=$(1)\
 $(INSTALLER_BUILDER_OPTIONS)\
 $(LOCAL_INSTALLER_BUILDER_OPTIONS)

# BUILD platform build-package-name install-package-name
BUILD=$(call INVOKE_GUB,$(1)) $(2)\
  && $(call INVOKE_INSTALLER_BUILDER,$(1)) $(3)

BUILD_PLATFORM = $(shell $(PYTHON) bin/build-platform)
OTHER_PLATFORMS=$(filter-out $(BUILD_PLATFORM), $(PLATFORMS))
