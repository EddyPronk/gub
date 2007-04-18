sources = GNUmakefile $(wildcard *.py specs/*.py lib/*.py)

default: compilers

PYTHON=python
CWD:=$(shell pwd)
INVOKE_GUB_BUILDER=$(PYTHON) gub-builder.py\
 --target-platform $(1)\
 $(foreach h,$(GUB_NATIVE_DISTCC_HOSTS), --native-distcc-host $(h))\
 $(foreach h,$(GUB_CROSS_DISTCC_HOSTS), --cross-distcc-host $(h))\
 $(LOCAL_GUB_BUILDER_OPTIONS)

INVOKE_GUP=$(PYTHON) gup-manager.py\
 --platform $(1)

include compilers.make

TAGS: $(sources)
	etags $^

MAKE_FILES = $(wildcard *.make)
MAKE_BASES = $(MAKE_FILES:%.make=%)

help:
	@echo Usage: make TAGS$(foreach a,$(MAKE_BASES),"|$a")
	@echo
	@echo For more elaborate use, see READMEs

$(MAKE_BASES):
	make -f $@.make

download-local:
