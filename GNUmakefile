
default: all

all: linux mac mingw

linux:
	python driver.py linux

mac:
	python driver.py darwin

mingw:
	python driver.py -V mingw

realclean:
	rm -rf src target

distclean: realclean
	echo NOT rm -rf downloads

sources = GNUmakefile $(wildcard *.py specs/*.py)
TAGS: $(sources)
	etags $^
