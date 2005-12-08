
default: all

all: linux mingw mac


# local.make should set the following variables:
#
#  LILYPOND_CVSDIR - a CVS HEAD working directory
#


include local.make


include $(LILYPOND_CVSDIR)/VERSION
LILYPOND_VERSION=$(MAJOR_VERSION).$(MINOR_VERSION).$(PATCH_LEVEL).$(if $(MY_PATCH_LEVEL),.$(MY_PATCH_LEVEL),)


INVOKE_DRIVER=python driver.py --version $(LILYPOND_VERSION)

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
