
default: all

all: linux mingw mac

linux:
	python driver.py --platform linux

mac:
	python driver.py --platform darwin

mingw:
	python driver.py -V --platform mingw

realclean:
	rm -rf src target

distclean: realclean
	echo NOT rm -rf downloads

sources = GNUmakefile $(wildcard *.py specs/*.py)
TAGS: $(sources)
	etags $^
