
.PHONY: all default distclean download test TAGS
.PHONY: cygwin darwin debian freebsd linux mac mingw

default: all

all: linux mingw mac

TEST_PLATFORMS=$(PLATFORMS)


# local.make should set the following variables:
#
#  LILYPOND_CVSDIR - a CVS HEAD working directory
#  LILYPOND_BRANCH - the tag for this branch, or HEAD 
#  BUILD_PLATFORM  - the platform used for building.
#  GUB_DISTCC_ALLOW_HOSTS - which distcc daemons may connect.
#  GUB_DISTCC_HOSTS - which distcc daemons may connect.


include local.make

include $(LILYPOND_CVSDIR)/VERSION



##LILYPOND_BRANCH=$(strip $(patsubst $(shell cd $(LILYPOND_CVSDIR) && expr "$$(cvs status ChangeLog)" : '.*Sticky Tag: *\([^ ]*\)'),(none),HEAD))

ifeq ($(LILYPOND_BRANCH),)
LILYPOND_BRANCH=$(shell (cat $(LILYPOND_CVSDIR)/CVS/Tag 2> /dev/null || echo HEAD) | sed s/^T//)
endif

PLATFORMS=darwin mingw linux freebsd
LILYPOND_VERSION=$(MAJOR_VERSION).$(MINOR_VERSION).$(PATCH_LEVEL)$(if $(strip $(MY_PATCH_LEVEL)),.$(MY_PATCH_LEVEL),)
INSTALLER_BUILD:=$(shell python lilypondorg.py nextbuild $(LILYPOND_VERSION))
INVOKE_DRIVER=python driver.py \
--target-platform $(1) \
--branch $(LILYPOND_BRANCH) \
$(foreach h,$(GUB_DISTCC_HOSTS), --distcc-host $(h))\
--installer-version $(LILYPOND_VERSION) \
--installer-build $(INSTALLER_BUILD) \
$(LOCAL_DRIVER_OPTIONS)

INVOKE_XPM=python xpm-apt.py \
--platform $(1) \
--branch $(LILYPOND_BRANCH) 

BUILD=$(call INVOKE_DRIVER,$(1)) build $(2) \
  && $(call INVOKE_DRIVER,$(1)) build-installer \
  && $(call INVOKE_DRIVER,$(1)) package-installer \

CWD:=$(shell pwd)

download:
	$(foreach p, $(PLATFORMS), $(call INVOKE_DRIVER,$(p)) download lilypond && ) true
	$(call INVOKE_DRIVER,mingw) download lilypad
	$(call INVOKE_DRIVER,darwin) download osx-lilypad
	$(call INVOKE_DRIVER,local) download flex nsis fakeroot pkg-config guile
	$(foreach p, $(PLATFORMS), (mv uploads/$(p)/lilypond-$(LILYPOND_BRANCH).$(p).gub uploads/$(p)/lilypond-$(LILYPOND_BRANCH)-OLD.$(p).gub || true) &&) true
	$(foreach p, $(PLATFORMS), $(call INVOKE_XPM,$(p)) remove lilypond ; ) true
	rm -f target/*/status/lilypond*
	rm -f log/lilypond-$(LILYPOND_VERSION)-$(INSTALLER_BUILD).*.test.pdf

all: linux freebsd mac mingw

arm:
	$(call BUILD,$@,lilypond)

cygwin:
	$(call BUILD,$@,lilypond)

darwin:
	$(call BUILD,$@,lilypond)

debian:
	$(call BUILD,$@,lilypond)

freebsd:
	$(call BUILD,$@,lilypond)

linux:
	$(call BUILD,$@,lilypond)

mac: darwin

mingw:
	$(call BUILD,$@,lilypad lilypond)

clean:
	rm -rf $(foreach p, $(PLATFORMS), target/*$(p)* )

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
	rm -rf $(foreach p,$(TEST_PLATFORMS), uploads/$(p)/*  target/*$(p)* )
	$(RUN_TEST) $(foreach p, $(TEST_PLATFORMS), "make $(p) from=$(BUILD_PLATFORM)")

release-test:
	$(foreach p,$(PLATFORMS), test-gub-build.py uploads/lilypond-$(LILYPOND_VERSION)-$(INSTALLER_BUILD).$(p)*[^2] && ) true


#FIXME: how to get libc+kernel headers package contents on freebsd?
# * remove zlib.h, zconf.h or include libz and remove Zlib from src packages?
# * remove gmp.h, or include libgmp and remove Gmp from src packages?
# bumb version number by hand, sync with freebsd.py
freebsd-runtime:
	ssh xs4all.nl tar -C / --exclude=zlib.h --exclude=zconf.h --exclude=gmp.h -czf public_html/freebsd-runtime-4.10-2.tar.gz /usr/lib/{lib{c,c_r,m}{.a,.so{,.*}},crt{i,n,1}.o} /usr/include


DISTCC_DIRS=target/distcc/bin/  target/distccd/bin/
distccd:
	chmod +x specs/distcc.py
	rm -rf $(DISTCC_DIRS)
	$(if $(wildcard log/distccd.pid),kill `cat log/distccd.pid`, true)
	mkdir -p $(DISTCC_DIRS)
	ln -s $(foreach p,$(PLATFORMS),$(CWD)/target/$(p)/system/usr/cross/bin/*) target/distccd/bin
	$(foreach binary,$(foreach p,$(PLATFORMS), $(wildcard target/$(p)/system/usr/cross/bin/*)), \
		ln -s $(CWD)/specs/distcc.py target/distcc/bin/$(notdir $(binary)) && ) true

	DISTCCD_PATH=$(CWD)/target/distccd/bin distccd --daemon $(addprefix --allow ,$(GUB_DISTCC_ALLOW_HOSTS)) \
		--daemon --port 3633 --pid-file $(CWD)/log/distccd.pid \
		--log-file $(CWD)/log/distccd.log  --log-level debug 

