
.PHONY: all default distclean download test TAGS
.PHONY: darwin freebsd linux mac mingw

default: all

all: linux mingw mac


# local.make should set the following variables:
#
#  LILYPOND_CVSDIR - a CVS HEAD working directory
#  LILYPOND_BRANCH - the tag for this branch, or HEAD 
#  BUILD_PLATFORM - the platform used for building.
#

include local.make

include $(LILYPOND_CVSDIR)/VERSION


##LILYPOND_BRANCH=$(strip $(patsubst $(shell cd $(LILYPOND_CVSDIR) && expr "$$(cvs status ChangeLog)" : '.*Sticky Tag: *\([^ ]*\)'),(none),HEAD))

## doesn't actually work for HEAD.

#LILYPOND_BRANCH=$(shell cat $(LILYPOND_CVSDIR)/CVS/Tag 2> /dev/null \
# | sed s/^T// || echo HEAD)

PLATFORMS=darwin mingw linux freebsd

LILYPOND_VERSION=$(MAJOR_VERSION).$(MINOR_VERSION).$(PATCH_LEVEL)$(if $(strip $(MY_PATCH_LEVEL)),.$(MY_PATCH_LEVEL),)

INVOKE_DRIVER=python driver.py \
--target-platform=$(1) \
--branch=$(LILYPOND_BRANCH) \
--build-platform=$(BUILD_PLATFORM) \
--installer-version=$(LILYPOND_VERSION) \
--installer-build=1 \
$(LOCAL_DRIVER_OPTIONS)

INVOKE_XPM=python xpm-apt.py \
--platform=$(1) 
--build-platform=$(BUILD_PLATFORM) \
--branch=$(LILYPOND_BRANCH)

BUILD_ALL=$(call INVOKE_DRIVER,$(1)) -t build all \
  && $(call INVOKE_XPM,$(1)) -t install all \
  && $(call INVOKE_DRIVER,$(1)) build all \
  && $(call INVOKE_XPM,$(1)) install all \
  && $(call INVOKE_DRIVER,$(1)) build-installer \
  && $(call INVOKE_DRIVER,$(1)) package-installer \


download:
	$(foreach p, $(PLATFORMS), $(call INVOKE_DRIVER,$(p)) download && ) true
	rm -f uploads/*/lilypond-$(LILYPOND_BRANCH)*gub
	$(foreach p, $(PLATFORMS), $(call INVOKE_XPM,$(p)) remove lilypond ; ) true

all: linux freebsd mac mingw

linux:
	$(call BUILD_ALL,$@)

freebsd:
	$(call BUILD_ALL,$@)

darwin:
	$(call BUILD_ALL,$@)

mac: darwin

mingw:
	$(call BUILD_ALL,$@) 

distclean:
	rm -rf target uploads

sources = GNUmakefile $(wildcard *.py specs/*.py)

TAGS: $(sources)
	etags $^

cyg-apt.py: cyg-apt.py.in specs/cpm.py
	sed -e "/@CPM@/r specs/cpm.py" -e "s/@CPM@//" < $< > $@
	chmod +x $@


## TODO: should put build platform in targetname too.
RUN_TEST=python test-gub.py --to hanwen@xs4all.nl --to janneke@gnu.org --smtp smtp.xs4all.nl "make $(1)" 
test:
	$(MAKE) distclean
	$(MAKE) download
	$(foreach p, $(PLATFORMS), $(call RUN_TEST,$(p)) && ) true
