
default: all

all: linux mingw mac


# local.make should set the following variables:
#
#  LILYPOND_CVSDIR - a CVS HEAD working directory
#  LILYPOND_MINGW_INSTALLER_DIR - previous incarnation of lilypond installer
#

include local.make


include $(LILYPOND_CVSDIR)/VERSION

LILYPOND_VERSION=$(MAJOR_VERSION).$(MINOR_VERSION).$(PATCH_LEVEL)$(if $(strip $(MY_PATCH_LEVEL)),.$(MY_PATCH_LEVEL),)


INVOKE_DRIVER=python driver.py \
--package-version=$(LILYPOND_VERSION) \
--package-build=1 \
--setting=lilywinbuilddir=$(LILYPOND_MINGW_INSTALLER_DIR) \
$(LOCAL_DRIVER_OPTIONS)

linux:
	$(INVOKE_DRIVER) --platform linux

mac:
	$(INVOKE_DRIVER) --platform darwin

mingw:
	$(INVOKE_DRIVER) --platform mingw

mingw-fedora:
	$(INVOKE_DRIVER) --platform mingw-fedora

realclean:
	rm -rf src target

distclean: realclean
	echo NOT rm -rf downloads

sources = GNUmakefile $(wildcard *.py specs/*.py)
TAGS: $(sources)
	etags $^

cyg-apt.py: cyg-apt.py.in specs/cpm.py
	sed -e "/@CPM@/r specs/cpm.py" -e "s/@CPM@//" < $< > $@
	chmod +x $@

test-cygwin: cyg-apt.py
	rm -f ~/.cyg-apt .cyg-apt
	rm -rf cygwin
	./cyg-apt.py setup
	./cyg-apt.py -x install cygwin
	./cyg-apt.py list

test-gub: cyg-apt.py
	rm -f ~/.cyg-apt .cyg-apt
	./cyg-apt.py --root=target/i686-mingw32/system --mirror=file://uploads setup --ini=file://uploads/setup.ini
	./cyg-apt.py list

gpm-install: test-gub
	./cyg-apt.py install $$(./cyg-apt.py available)
	