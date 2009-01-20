.PHONY: lilypond mingit phone web
.PHONY: default compilers TAGS help
sources = GNUmakefile $(filter-out %~, $(wildcard *.make bin/* gub/*.py gub/*/*.py gub/*/*/*.py gub/*/*/*/*.py test-lily/*.py))

ifeq ($(PLATFORMS),)
# linux-ppc broken
PLATFORMS=linux-x86 darwin-ppc darwin-x86 mingw linux-64 linux-ppc freebsd-x86 freebsd-64
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

gub3% lily% cygwin%:
	$(MAKE) -f lilypond.make $@

test:
	rm -rf target
	make -f lilypond.make tools LOCAL_GUB_OPTIONS=-vvv
	bin/gub -p $(BUILD_PLATFORM) --branch=lilypond=master:master lilypond -vvv

README: web/index.html web/lilypond.html
	w3m -dump $^ > $@

web: README
	scp -p web/*html lilypond.org:/var/www/lilypond/gub

PYTHON_SOURCES = $$(git ls-files | grep -E '(^bin/|*.py$$)')
python3:
# a 2to3 crash fails to convert the remaining files
#	2to3-3.0 -nw $(PYTHON_SOURCES) >/dev/null || :
	for i in $(PYTHON_SOURCES); do\
	    2to3-3.0 -nw $$i >/dev/null || :; \
	done
	sed -i -e 's@\t@        @g' \
	    -e 's@\(list\|print\)(@\1 (@g' \
	    -e 's@import md5@import hashlib@g' \
	    -e 's@md5[.]md5@hashlib.md5@g' \
	    -e 's@md5[.]new@hashlib.md5.new@g' \
	    -e 's@import new@import gub.new3@g' \
	    -e 's@new[.]@new3.@g' \
		$(PYTHON_SOURCES)
