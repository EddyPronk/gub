.PHONY: lilypond mingit phone web
.PHONY: default compilers TAGS help
sources = GNUmakefile $(filter-out %~, $(wildcard *.make bin/* gub/*.py gub/*/*.py gub/*/*/*.py gub/*/*/*/*.py test-lily/*.py))

ifeq ($(PLATFORMS),)
PLATFORMS=linux-x86 linux-64 linux-ppc freebsd-x86 freebsd-64 darwin-ppc darwin-x86 mingw
endif

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

test:
	rm -rf target
	make -f lilypond.make tools LOCAL_GUB_OPTIONS=-vvv
	bin/gub -p $(BUILD_PLATFORM) --branch=lilypond=master:master lilypond -vvv

README: web/index.html web/lilypond.html
	w3m -dump $^ > $@

web:
	scp -p web/*html lilypond.org:/var/www/lilypond/gub
