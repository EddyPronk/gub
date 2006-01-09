
.PHONY: all default distclean download test TAGS
.PHONY: darwin freebsd linux mac mingw

default: all

all: linux mingw mac


# local.make should set the following variables:
#
#  LILYPOND_CVSDIR - a CVS HEAD working directory
#  LILYPOND_BRANCH - the tag for this branch, or HEAD 
#

include local.make

include $(LILYPOND_CVSDIR)/VERSION
INSTALLER_BUILD=1


##LILYPOND_BRANCH=$(strip $(patsubst $(shell cd $(LILYPOND_CVSDIR) && expr "$$(cvs status ChangeLog)" : '.*Sticky Tag: *\([^ ]*\)'),(none),HEAD))

LILYPOND_BRANCH=$(shell (cat $(LILYPOND_CVSDIR)/CVS/Tag 2> /dev/null || echo HEAD) | sed s/^T//)

PLATFORMS=darwin mingw linux freebsd

LILYPOND_VERSION=$(MAJOR_VERSION).$(MINOR_VERSION).$(PATCH_LEVEL)$(if $(strip $(MY_PATCH_LEVEL)),.$(MY_PATCH_LEVEL),)

INVOKE_DRIVER=python driver.py \
--target-platform=$(1) \
--branch=$(LILYPOND_BRANCH) \
--installer-version=$(LILYPOND_VERSION) \
--installer-build=$(INSTALLER_BUILD) \
$(LOCAL_DRIVER_OPTIONS)

INVOKE_XPM=python xpm-apt.py \
--platform=$(1) 
--branch=$(LILYPOND_BRANCH)

BUILD=$(call INVOKE_DRIVER,$(1)) build $(2) \
  && $(call INVOKE_XPM,$(1)) install $(2) \
  && $(call INVOKE_DRIVER,$(1)) build-installer \
  && $(call INVOKE_DRIVER,$(1)) package-installer \


download:
	$(foreach p, $(PLATFORMS), $(call INVOKE_DRIVER,$(p)) download lilypond && ) true
	$(call INVOKE_DRIVER,mingw) download lilypad
	$(call INVOKE_DRIVER,darwin) download osx-lilypad
	$(call INVOKE_DRIVER,local) download flex nsis fakeroot pkg-config guile 

	$(foreach p, $(PLATFORMS), (mv uploads/$(p)/lilypond-$(LILYPOND_BRANCH).$(p).gub uploads/$(p)/lilypond-$(LILYPOND_BRANCH)-OLD.$(p).gub || true) &&) true
	$(foreach p, $(PLATFORMS), $(call INVOKE_XPM,$(p)) remove lilypond ; ) true
	rm -f target/*/status/lilypond*

all: linux freebsd mac mingw

darwin:
	$(call BUILD,$@,ghostscript lilypond osx-lilypad)

debian:
	$(call BUILD,$@,lilypond)

freebsd:
	$(call BUILD,$@,lilypond)

linux:
	$(call BUILD,$@,lilypond)

mac: darwin

mingw:
	$(call BUILD,$@,lilypad lilypond)

realclean:
	rm -rf $(foreach p, $(PLATFORMS), uploads/$(p)/*  target/*$(p)* )

sources = GNUmakefile $(wildcard *.py specs/*.py)

TAGS: $(sources)
	etags $^

cyg-apt.py: cyg-apt.py.in specs/cpm.py
	sed -e "/@CPM@/r specs/cpm.py" -e "s/@CPM@//" < $< > $@
	chmod +x $@


## TODO: should LilyPond revision in targetname too.
RUN_TEST=python test-gub.py --to hanwen@xs4all.nl --to janneke@gnu.org --smtp smtp.xs4all.nl 
test:
	$(MAKE) realclean
	$(RUN_TEST) $(foreach p, $(PLATFORMS), "make $(p) from=$(BUILD_PLATFORM)")

#FIXME: how to get libc+kernel headers package contents on freebsd?
# * remove zlib.h, zconf.h or include libz and remove Zlib from src packages?
# * remove gmp.h, or include libgmp and remove Gmp from src packages?
# bumb version number by hand, sync with freebsd.py
freebsd-runtime:
	ssh xs4all.nl tar -C / --exclude=zlib.h --exclude=zconf.h --exclude=gmp.h -czf public_html/freebsd-runtime-4.10-2.tar.gz /usr/lib/{lib{c,c_r,m}{.a,.so{,.*}},crt{i,n,1}.o} /usr/include
