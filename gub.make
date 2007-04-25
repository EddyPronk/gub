CWD:=$(shell pwd)
PYTHON=python
PYTHONPATH=lib/
export PYTHONPATH

## must always have one host.
GUB_DISTCC_ALLOW_HOSTS=127.0.0.1

GUB_BUILDER = $(PYTHON) gub-builder.py
INVOKE_GUB_BUILDER=$(GUB_BUILDER)\
 --target-platform $(1)\
 $(foreach h,$(GUB_NATIVE_DISTCC_HOSTS), --native-distcc-host $(h))\
 $(foreach h,$(GUB_CROSS_DISTCC_HOSTS), --cross-distcc-host $(h))\
 $(GUB_BUILDER_OPTIONS)\
 $(LOCAL_GUB_BUILDER_OPTIONS)

GUP_MANAGER = $(PYTHON) gup-manager.py
INVOKE_GUP=$(GUP_MANAGER)\
 --platform $(1)\
 $(GUP_OPTIONS)

INSTALLER_BUILDER = $(PYTHON) installer-builder.py
INVOKE_INSTALLER_BUILDER=$(INSTALLER_BUILDER)\
 --target-platform $(1)\
 $(INSTALLER_BUILDER_OPTIONS)

BUILD=$(call INVOKE_GUB_BUILDER,$(1)) --offline $(2)\
  && $(call INVOKE_INSTALLER_BUILDER,$(1)) build-all $(PACKAGE)

OTHER_PLATFORMS=$(filter-out $(BUILD_PLATFORM), $(PLATFORMS))
