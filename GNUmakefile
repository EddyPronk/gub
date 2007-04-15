sources = GNUmakefile $(wildcard *.py specs/*.py lib/*.py)

TAGS: $(sources)
	etags $^

MAKE_FILES = $(wildcard *.make)
MAKE_BASES = $(MAKE_FILES:%.make=%)

help:
	@echo Usage: make TAGS$(foreach a,$(MAKE_BASES),"|$a")

$(MAKE_BASES):
	make -f $@.make
