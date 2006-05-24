
.PHONY: all default distclean download test TAGS
.PHONY: cygwin darwin-ppc darwin-x86 debian freebsd linux mingw bootstrap-download bootstrap
.PHONY: update-buildnumber

default: all



TEST_PLATFORMS=$(PLATFORMS)

## must always have one host.
GUB_DISTCC_ALLOW_HOSTS=127.0.0.1
PLATFORMS=darwin-ppc darwin-x86 mingw linux freebsd cygwin

LILYPOND_CVSDIR=downloads/lilypond-$(BRANCH)/
LILYPOND_BRANCH=$(BRANCH)
BRANCH=HEAD

OTHER_PLATFORMS=$(filter-out $(BUILD_PLATFORM), $(PLATFORMS))

INVOKE_GUB_BUILDER=$(PYTHON) gub-builder.py \
--target-platform $(1) \
--branch $(LILYPOND_BRANCH) \
$(foreach h,$(GUB_NATIVE_DISTCC_HOSTS), --native-distcc-host $(h))\
$(foreach h,$(GUB_CROSS_DISTCC_HOSTS), --cross-distcc-host $(h))\
$(LOCAL_GUB_OPTIONS)

INVOKE_GUP=$(PYTHON) gup-manager.py \
--platform $(1) \
--branch $(LILYPOND_BRANCH) 

INVOKE_INSTALLER_BUILDER=$(PYTHON) installer-builder.py \
  --target-platform $(1) \
  --branch $(LILYPOND_BRANCH) \

BUILD=$(call INVOKE_GUB_BUILDER,$(1)) build $(2) \
  && $(call INVOKE_INSTALLER_BUILDER,$(1)) build \
  && $(call INVOKE_INSTALLER_BUILDER,$(1)) strip \
  && $(call INVOKE_INSTALLER_BUILDER,$(1)) package \

CWD:=$(shell pwd)

DISTCC_DIRS=target/cross-distcc/bin/  target/cross-distccd/bin/ target/native-distcc/bin/ 

PYTHON=python
sources = GNUmakefile $(wildcard *.py specs/*.py lib/*.py)

NATIVE_TARGET_DIR=$(CWD)/target/$(BUILD_PLATFORM)/
BUILDNUMBER_FILE = buildnumber-$(LILYPOND_BRANCH).make

## TODO: should LilyPond revision in targetname too.
RUN_TEST=$(PYTHON) test-gub.py --summary --tag-repo abc.webdev.nl:/home/hanwen/repo/gub-tags --to hanwen@xs4all.nl --to janneke-list@xs4all.nl --smtp smtp.xs4all.nl 

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
  bootstrap-download: update-buildnumber
	  $(PYTHON) gub-builder.py -p linux download

else

  ################
  # ensuing runs, we have CVS.

  include $(LILYPOND_CVSDIR)/VERSION

  LILYPOND_VERSION=$(MAJOR_VERSION).$(MINOR_VERSION).$(PATCH_LEVEL)$(if $(strip $(MY_PATCH_LEVEL)),.$(MY_PATCH_LEVEL),)

  bootstrap-download: 

  include $(BUILDNUMBER_FILE)

endif

UPDATE-BUILDNUMBER=(echo -n "INSTALLER_BUILD=" && \
		$(PYTHON) lilypondorg.py nextbuild $(LILYPOND_VERSION) ) > buildnumber.tmp && \
		mv buildnumber.tmp $(BUILDNUMBER_FILE)

$(BUILDNUMBER_FILE):
	$(UPDATE-BUILDNUMBER)

download:
	$(UPDATE-BUILDNUMBER)
	$(foreach p, $(PLATFORMS), $(call INVOKE_GUB_BUILDER,$(p)) download lilypond && ) true
	$(call INVOKE_GUB_BUILDER,mingw) download lilypad
	$(call INVOKE_GUB_BUILDER,darwin-ppc) download osx-lilypad
	rm -f target/*/status/lilypond*
	rm -f log/lilypond-$(LILYPOND_VERSION)-$(INSTALLER_BUILD).*.test.pdf

all: $(BUILD_PLATFORM) doc $(OTHER_PLATFORMS) gub_builder.py

gub_builder.py:
	ln -s gub-builder.py $@

arm:
	$(call BUILD,$@,lilypond)

cygwin: doc
	rm -rf uploads/cygwin/*guile*
	$(call INVOKE_GUB_BUILDER,$@) --build-source build guile
	$(PYTHON) gup-manager.py -p cygwin remove guile
	$(call INVOKE_GUB_BUILDER,$@) --build-source --split-packages build guile
	$(call INVOKE_INSTALLER_BUILDER,$@) --build-source --split-packages package guile
	$(call INVOKE_GUB_BUILDER,$@) --build-source build lilypond
	$(call INVOKE_INSTALLER_BUILDER,$@) --build-source build lilypond
	$(call INVOKE_INSTALLER_BUILDER,$@) --build-source strip lilypond
	$(call INVOKE_INSTALLER_BUILDER,$@) --build-source package lilypond

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
	$(foreach p, $(PLATFORMS),$(call INVOKE_GUB_BUILDER, $(p)) build gcc && ) true

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
