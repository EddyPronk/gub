.PHONY: lilypond mingit phone
.PHONY: default compilers TAGS help local download-local
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

download-local:
