
.PHONY: all default distclean download test TAGS
.PHONY: cygwin darwin-ppc darwin-x86 debian freebsd linux mingw

default: all


TEST_PLATFORMS=$(PLATFORMS)


# skip darwin-x86 ; still broken.
PLATFORMS=darwin-ppc mingw linux freebsd cygwin 
LILYPOND_VERSION=$(MAJOR_VERSION).$(MINOR_VERSION).$(PATCH_LEVEL)$(if $(strip $(MY_PATCH_LEVEL)),.$(MY_PATCH_LEVEL),)
INVOKE_DRIVER=python gub-builder.py \
--target-platform $(1) \
--branch $(LILYPOND_BRANCH) \
$(foreach h,$(GUB_NATIVE_DISTCC_HOSTS), --native-distcc-host $(h))\
$(foreach h,$(GUB_CROSS_DISTCC_HOSTS), --cross-distcc-host $(h))\
--installer-version $(LILYPOND_VERSION) \
--installer-build $(INSTALLER_BUILD) \
$(LOCAL_DRIVER_OPTIONS)

INVOKE_GUP=python gup-manager.py \
--platform $(1) \
--branch $(LILYPOND_BRANCH) 

BUILD=$(call INVOKE_DRIVER,$(1)) build $(2) \
  && $(call INVOKE_DRIVER,$(1)) build-installer \
  && $(call INVOKE_DRIVER,$(1)) strip-installer \
  && $(call INVOKE_DRIVER,$(1)) package-installer \

CWD:=$(shell pwd)

DISTCC_DIRS=target/cross-distcc/bin/  target/cross-distccd/bin/ target/native-distcc/bin/ 


sources = GNUmakefile $(wildcard *.py specs/*.py lib/*.py)

NATIVE_TARGET_DIR=$(CWD)/target/$(BUILD_PLATFORM)/

## TODO: should LilyPond revision in targetname too.
RUN_TEST=python test-gub.py --to hanwen@xs4all.nl --to janneke@gnu.org --smtp smtp.xs4all.nl 

# local.make should set the following variables:
#
#  LILYPOND_CVSDIR - a CVS HEAD working directory
#  LILYPOND_BRANCH - the tag for this branch, or HEAD 
#  BUILD_PLATFORM  - the platform used for building.
#  GUB_DISTCC_ALLOW_HOSTS - which distcc daemons may connect.
#  GUB_CROSS_DISTCC_HOSTS - hosts with matching cross compilers
#  GUB_NATIVE_DISTCC_HOSTS - hosts with matching native compilers
# 
include local.make
include $(LILYPOND_CVSDIR)/VERSION

ifeq ($(LILYPOND_BRANCH),)
LILYPOND_BRANCH=$(shell (cat $(LILYPOND_CVSDIR)/CVS/Tag 2> /dev/null || echo HEAD) | sed s/^T//)
endif
INSTALLER_BUILD:=$(shell python lilypondorg.py nextbuild $(LILYPOND_VERSION))


download:
	$(foreach p, $(PLATFORMS), $(call INVOKE_DRIVER,$(p)) download lilypond && ) true
	$(call INVOKE_DRIVER,mingw) download lilypad
	$(call INVOKE_DRIVER,darwin-ppc) download osx-lilypad
	$(call INVOKE_DRIVER,local) download flex mftrace potrace fontforge \
		guile pkg-config nsis icoutils
	$(foreach p, $(PLATFORMS), (mv uploads/$(p)/lilypond-$(LILYPOND_BRANCH).$(p).gub uploads/$(p)/lilypond-$(LILYPOND_BRANCH)-OLD.$(p).gub || true) &&) true
	$(foreach p, $(PLATFORMS), $(call INVOKE_GUP,$(p)) remove lilypond ; ) true
	rm -f target/*/status/lilypond*
	rm -f log/lilypond-$(LILYPOND_VERSION)-$(INSTALLER_BUILD).*.test.pdf

all: linux darwin-ppc doc freebsd mingw doc

arm:
	$(call BUILD,$@,lilypond)

cygwin:
	$(call BUILD,$@,guile lilypond)

darwin-ppc:
	$(call BUILD,$@,lilypond)

darwin-x86:
	$(call BUILD,$@,lilypond)

debian:
	$(call BUILD,$@,lilypond)

freebsd:
	$(call BUILD,$@,lilypond)

linux:
	$(call BUILD,$@,lilypond)

mingw:
	$(call BUILD,$@,lilypad lilypond)

clean:
	rm -rf $(foreach p, $(PLATFORMS), target/*$(p)* )

realclean:
	rm -rf $(foreach p, $(PLATFORMS), uploads/$(p)/* uploads/$(p)-cross/* target/*$(p)* )

TAGS: $(sources)
	etags $^

cyg-apt.py: cyg-apt.py.in specs/cpm.py
	sed -e "/@CPM@/r specs/cpm.py" -e "s/@CPM@//" < $< > $@
	chmod +x $@


test:
	make realclean PLATFORMS="$(TEST_PLATFORMS)"
	$(RUN_TEST) $(foreach p, $(TEST_PLATFORMS), "make $(p) from=$(BUILD_PLATFORM)")

release-test:
	$(foreach p,$(PLATFORMS), test-gub-build.py uploads/lilypond-$(LILYPOND_VERSION)-$(INSTALLER_BUILD).$(p)*[^2] && ) true


#FIXME: how to get libc+kernel headers package contents on freebsd?
# * remove zlib.h, zconf.h or include libz and remove Zlib from src packages?
# * remove gmp.h, or include libgmp and remove Gmp from src packages?
# bumb version number by hand, sync with freebsd.py
freebsd-runtime:
	ssh xs4all.nl tar -C / --exclude=zlib.h --exclude=zconf.h --exclude=gmp.h -czf public_html/freebsd-runtime-4.10-2.tar.gz /usr/lib/{lib{c,c_r,m}{.a,.so{,.*}},crt{i,n,1}.o} /usr/include


distccd: clean-distccd cross-distccd native-distccd local-distcc

clean-distccd:
	rm -rf $(DISTCC_DIRS)
	mkdir -p $(DISTCC_DIRS)

local-distcc:
	chmod +x lib/distcc.py
	$(foreach binary,$(foreach p,$(PLATFORMS), $(wildcard target/$(p)/system/usr/cross/bin/*)), \
		ln -s $(CWD)/lib/distcc.py target/cross-distcc/bin/$(notdir $(binary)) && ) true
	$(foreach binary, gcc g++, \
		ln -s $(CWD)/lib/distcc.py target/native-distcc/bin/$(notdir $(binary)) && ) true

cross-distccd:
	$(foreach p, $(PLATFORMS),$(call INVOKE_DRIVER, $(p)) build gcc && ) true
	-$(if $(wildcard log/$@.pid),kill `cat log/$@.pid`, true)
	ln -s $(foreach p,$(PLATFORMS),$(wildcard $(CWD)/target/$(p)/system/usr/cross/bin/*)) target/cross-distccd/bin

	DISTCCD_PATH=$(CWD)/target/cross-distccd/bin distccd --daemon $(addprefix --allow ,$(GUB_DISTCC_ALLOW_HOSTS)) \
		--port 3633 --pid-file $(CWD)/log/$@.pid \
		--log-file $(CWD)/log/cross-distccd.log  --log-level info

native-distccd:
	-$(if $(wildcard log/$@.pid),kill `cat log/$@.pid`, true)
	distccd --daemon $(addprefix --allow ,$(GUB_DISTCC_ALLOW_HOSTS)) \
		--port 3634 --pid-file $(CWD)/log/$@.pid \
		--log-file $(CWD)/log/$@.log  --log-level info



# gs 8.50 ?
#	PATH=$(NATIVE_TARGET_DIR)/system/usr/bin/:$(PATH) \
#		GS_LIB=$(NATIVE_TARGET_DIR)/system/usr/share/ghostscript/8.50/lib/ \

doc-clean:
	make -C $(NATIVE_TARGET_DIR)/build/lilypond-$(LILYPOND_BRANCH) \
			DOCUMENTATION=yes web-clean

doc-update:
	python gub-builder.py -p $(BUILD_PLATFORM) download lilypond
	python gup-manager.py  -p $(BUILD_PLATFORM) remove lilypond
	python gub-builder.py -p $(BUILD_PLATFORM) --stage untar build lilypond
	rm -f target/$(BUILD_PLATFORM)/status/lilypond*

doc:
	unset LILYPONDPREFIX \
	  && make -C $(NATIVE_TARGET_DIR)/build/lilypond-$(LILYPOND_BRANCH)  \
	  LILYPOND_EXTERNAL_BINARY=$(NATIVE_TARGET_DIR)/system/usr/bin/lilypond \
	  DOCUMENTATION=yes web 
	tar -C target/$(BUILD_PLATFORM)/build/lilypond-$(LILYPOND_BRANCH)/out-www/web-root/ -cjf $(CWD)/uploads/lilypond-$(LILYPOND_VERSION)-$(INSTALLER_BUILD).documentation.tar.bz2 .


bootstrap:
	python gub-builder.py -p local download flex mftrace potrace fontforge \
	   guile pkg-config nsis icoutils
	python gub-builder.py -p local build flex mftrace potrace fontforge \
	   guile pkg-config
	make distccd
	python gub-builder.py -p local build nsis icoutils
	$(MAKE) download
