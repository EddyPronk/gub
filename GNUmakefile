
.PHONY: all default distclean download test TAGS
.PHONY: cygwin darwin-ppc darwin-x86 debian freebsd linux mingw bootstrap-download bootstrap

default: all



TEST_PLATFORMS=$(PLATFORMS)

## must always have one host.
GUB_DISTCC_ALLOW_HOSTS=127.0.0.1
PLATFORMS=darwin-ppc darwin-x86 mingw linux freebsd cygwin

LILYPOND_CVSDIR=downloads/lilypond-$(BRANCH)/
LILYPOND_BRANCH=$(BRANCH)
BRANCH=HEAD

OTHER_PLATFORMS=$(filter-out $(BUILD_PLATFORM), $(PLATFORMS))

INVOKE_DRIVER=$(PYTHON) gub-builder.py \
--target-platform $(1) \
--branch $(LILYPOND_BRANCH) \
$(foreach h,$(GUB_NATIVE_DISTCC_HOSTS), --native-distcc-host $(h))\
$(foreach h,$(GUB_CROSS_DISTCC_HOSTS), --cross-distcc-host $(h))\
--installer-version $(LILYPOND_VERSION) \
--installer-build $(INSTALLER_BUILD) \
$(LOCAL_DRIVER_OPTIONS)

INVOKE_GUP=$(PYTHON) gup-manager.py \
--platform $(1) \
--branch $(LILYPOND_BRANCH) 

BUILD=$(call INVOKE_DRIVER,$(1)) build $(2) \
  && $(call INVOKE_DRIVER,$(1)) build-installer \
  && $(call INVOKE_DRIVER,$(1)) strip-installer \
  && $(call INVOKE_DRIVER,$(1)) package-installer \

CWD:=$(shell pwd)

DISTCC_DIRS=target/cross-distcc/bin/  target/cross-distccd/bin/ target/native-distcc/bin/ 

PYTHON=python
sources = GNUmakefile $(wildcard *.py specs/*.py lib/*.py)

NATIVE_TARGET_DIR=$(CWD)/target/$(BUILD_PLATFORM)/

## TODO: should LilyPond revision in targetname too.
RUN_TEST=$(PYTHON) test-gub.py --tag-repo abc.webdev.nl:repo/gub-tags --to hanwen@xs4all.nl --to janneke-list@xs4all.nl --smtp smtp.xs4all.nl 

# local.make should set the following variables:
#
#  BUILD_PLATFORM  - the platform used for building.
#  GUB_DISTCC_ALLOW_HOSTS - which distcc daemons may connect.
#  GUB_CROSS_DISTCC_HOSTS - hosts with matching cross compilers
#  GUB_NATIVE_DISTCC_HOSTS - hosts with matching native compilers
#
ifneq ($(wildcard local.make),)
  include local.make
endif


ifeq ($(wildcard $(LILYPOND_CVSDIR)),)

  ################
  # first installation, no LilyPond CVS yet.

  LILYPOND_VERSION=0.0.0

  bootstrap: bootstrap-download

  ## need to download CVS before we can actually start doing anything.
  bootstrap-download:
	  $(PYTHON) gub-builder.py -p linux download

else

  ################
  # ensuing runs, we have CVS.

  include $(LILYPOND_CVSDIR)/VERSION

  LILYPOND_VERSION=$(MAJOR_VERSION).$(MINOR_VERSION).$(PATCH_LEVEL)$(if $(strip $(MY_PATCH_LEVEL)),.$(MY_PATCH_LEVEL),)

  bootstrap-download:

  ifeq ($(OFFLINE),)
    INSTALLER_BUILD:=$(shell $(PYTHON) lilypondorg.py nextbuild $(LILYPOND_VERSION))
  else
    INSTALLER_BUILD:=0
  endif
endif


download: 
	$(foreach p, $(PLATFORMS), $(call INVOKE_DRIVER,$(p)) download lilypond && ) true
	$(call INVOKE_DRIVER,mingw) download lilypad
	$(call INVOKE_DRIVER,darwin-ppc) download osx-lilypad
	rm -f target/*/status/lilypond*
	rm -f log/lilypond-$(LILYPOND_VERSION)-$(INSTALLER_BUILD).*.test.pdf

all: $(BUILD_PLATFORM) doc $(OTHER_PLATFORMS) gub_builder.py

gub_builder.py:
	ln -s gub-builder.py $@

arm:
	$(call BUILD,$@,lilypond)

cygwin: doc
	rm -rf uploads/cygwin/*guile*
	$(call INVOKE_DRIVER,$@) --build-source build guile
	$(PYTHON) gup-manager.py -p cygwin remove guile
	$(call INVOKE_DRIVER,$@) --build-source --split-packages build guile
	$(call INVOKE_DRIVER,$@) --build-source --split-packages package-installer guile
	$(call INVOKE_DRIVER,$@) --build-source build lilypond
	$(call INVOKE_DRIVER,$@) --build-source build-installer lilypond
	$(call INVOKE_DRIVER,$@) --build-source strip-installer lilypond
	$(call INVOKE_DRIVER,$@) --build-source package-installer lilypond

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

test:
	make realclean PLATFORMS="$(TEST_PLATFORMS)"
	$(RUN_TEST) $(foreach p, $(TEST_PLATFORMS), "make $(p) from=$(BUILD_PLATFORM)")

release-test:
	$(foreach p,$(PLATFORMS), $(PYTHON) test-lily/test-gub-build.py uploads/lilypond-$(LILYPOND_VERSION)-$(INSTALLER_BUILD).$(p) && ) true


distccd: clean-distccd cross-distccd-compilers cross-distccd native-distccd local-distcc

clean-distccd:
	rm -rf $(DISTCC_DIRS)
	mkdir -p $(DISTCC_DIRS)

local-distcc:
	chmod +x lib/distcc.py
	rm -rf target/native-distcc/bin/ target/cross-distcc/bin/
	mkdir -p target/cross-distcc/bin/ target/native-distcc/bin/
	$(foreach binary,$(foreach p,$(PLATFORMS), $(wildcard target/$(p)/system/usr/cross/bin/*)), \
		ln -s $(CWD)/lib/distcc.py target/cross-distcc/bin/$(notdir $(binary)) && ) true
	$(foreach binary, gcc g++, \
		ln -s $(CWD)/lib/distcc.py target/native-distcc/bin/$(notdir $(binary)) && ) true

cross-distccd-compilers:
	$(foreach p, $(PLATFORMS),$(call INVOKE_DRIVER, $(p)) build gcc && ) true

cross-distccd:
	-$(if $(wildcard log/$@.pid),kill `cat log/$@.pid`, true)
	rm -rf target/cross-distccd/bin/
	mkdir -p target/cross-distccd/bin/
	ln -s $(foreach p,$(PLATFORMS),$(wildcard $(CWD)/target/$(p)/system/usr/cross/bin/*)) target/cross-distccd/bin

	DISTCCD_PATH=$(CWD)/target/cross-distccd/bin distccd --daemon $(addprefix --allow ,$(GUB_DISTCC_ALLOW_HOSTS)) \
		--port 3633 --pid-file $(CWD)/log/$@.pid \
		--log-file $(CWD)/log/cross-distccd.log  --log-level info

native-distccd:
	-$(if $(wildcard log/$@.pid),kill `cat log/$@.pid`, true)
	distccd --daemon $(addprefix --allow ,$(GUB_DISTCC_ALLOW_HOSTS)) \
		--port 3634 --pid-file $(CWD)/log/$@.pid \
		--log-file $(CWD)/log/$@.log  --log-level info

doc-clean:
	make -C $(NATIVE_TARGET_DIR)/build/lilypond-$(LILYPOND_BRANCH) \
		DOCUMENTATION=yes web-clean

doc-update:
	$(PYTHON) gub-builder.py --branch $(LILYPOND_BRANCH) \
		-p $(BUILD_PLATFORM) download lilypond
	$(PYTHON) gup-manager.py --branch $(LILYPOND_BRANCH) \
		-p $(BUILD_PLATFORM) remove lilypond
	$(PYTHON) gub-builder.py --branch $(LILYPOND_BRANCH) \
		-p $(BUILD_PLATFORM) --stage untar build lilypond
	rm -f target/$(BUILD_PLATFORM)/status/lilypond*

NATIVE_LILY_BUILD=$(NATIVE_TARGET_DIR)/build/lilypond-$(LILYPOND_BRANCH)
NATIVE_ROOT=$(NATIVE_TARGET_DIR)/installer/

doc: $(BUILD_PLATFORM) doc-build

doc-build:
	unset LILYPONDPREFIX \
	  && make -C $(NATIVE_LILY_BUILD) \
	  LILYPOND_EXTERNAL_BINARY="$(NATIVE_ROOT)/usr/bin/lilypond"\
	  PATH=$(CWD)/target/local/system/usr/bin/:$(PATH) \
	  DOCUMENTATION=yes web 
	tar -C $(NATIVE_LILY_BUILD)/out-www/web-root/ \
		-cjf $(CWD)/uploads/lilypond-$(LILYPOND_VERSION)-$(INSTALLER_BUILD).documentation.tar.bz2 .

bootstrap:
	$(PYTHON) gub-builder.py $(LOCAL_DRIVER_OPTIONS) -p local download flex mftrace potrace fontforge \
	   guile pkg-config nsis icoutils fontconfig expat gettext
	$(PYTHON) gub-builder.py $(LOCAL_DRIVER_OPTIONS) -p local build flex mftrace potrace fontforge \
	   guile pkg-config fontconfig expat icoutils glib
	make distccd
	$(PYTHON) gub-builder.py $(LOCAL_DRIVER_OPTIONS) -p local build nsis 
	$(MAKE) download
