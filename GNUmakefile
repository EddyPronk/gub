
default: all

all: linux mingw mac


# local.make should set the following variables:
#
#  LILYPOND_CVSDIR - a CVS HEAD working directory
#


include local.make


include $(LILYPOND_CVSDIR)/VERSION
LILYPOND_VERSION=$(MAJOR_VERSION).$(MINOR_VERSION).$(PATCH_LEVEL).$(if $(MY_PATCH_LEVEL),.$(MY_PATCH_LEVEL),)


INVOKE_DRIVER=python driver.py --package-version $(LILYPOND_VERSION)

linux:
	$(INVOKE_DRIVER) --platform linux

mac:
	$(INVOKE_DRIVER) --platform darwin

mingw:
	$(INVOKE_DRIVER) --platform mingw

realclean:
	rm -rf src target

distclean: realclean
	echo NOT rm -rf downloads

sources = GNUmakefile $(wildcard *.py specs/*.py)
TAGS: $(sources)
	etags $^
