.PHONY: lilypond mingit phone
.PHONY: default compilers TAGS help tools download download-tools
sources = GNUmakefile $(filter-out %~, $(wildcard *.make bin/* gub/*.py gub/*/*.py gub/*/*/*.py gub/*/*/*/*.py))

default: compilers

include gub.make
include compilers.make

TAGS: $(sources)
	etags $^

MAKE_FILES = $(filter-out compilers.make gub.make local.make,$(wildcard *.make))
MAKE_BASES = $(MAKE_FILES:%.make=%)

help:
	@echo Usage: make TAGS$(foreach a,$(MAKE_BASES),"|$a")
	@echo
	@echo For more elaborate use, see READMEs

$(MAKE_BASES):
	$(MAKE) -f $@.make

download-tools:

download:
	$(foreach p, $(PLATFORMS), $(call INVOKE_GUB,$(p)) --online --stage=download $(call gcc_or_glibc,$(p)) && ) true

test:
	rm -rf target
	make -f lilypond.make tools LOCAL_GUB_OPTIONS=-vvv
	bin/gub -p $(BUILD_PLATFORM) --branch=lilypond=master:master lilypond -vvv
