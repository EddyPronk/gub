
.PHONY: all default distclean download TAGS
.PHONY: cygwin darwin-ppc darwin-x86 debian freebsd linux mingw bootstrap-download bootstrap
.PHONY: update-buildnumber

default: all



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
  --installer-version $(LILYPOND_VERSION) \
  --installer-build $(INSTALLER_BUILD) \
  --branch $(LILYPOND_BRANCH) \

BUILD=$(call INVOKE_GUB_BUILDER,$(1)) build $(2) \
  && $(call INVOKE_INSTALLER_BUILDER,$(1)) build-all lilypond

CWD:=$(shell pwd)

DISTCC_DIRS=target/cross-distcc/bin/  target/cross-distccd/bin/ target/native-distcc/bin/ 

PYTHON=python
sources = GNUmakefile $(wildcard *.py specs/*.py lib/*.py)

NATIVE_TARGET_DIR=$(CWD)/target/$(BUILD_PLATFORM)/
BUILDNUMBER_FILE = buildnumber-$(LILYPOND_BRANCH).make

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
	  $(PYTHON) gub-builder.py -p linux download lilypond

else


  ################
  # ensuing runs, we have CVS.

  include $(LILYPOND_CVSDIR)/VERSION

  LILYPOND_VERSION=$(MAJOR_VERSION).$(MINOR_VERSION).$(PATCH_LEVEL)$(if $(strip $(MY_PATCH_LEVEL)),.$(MY_PATCH_LEVEL),)

  bootstrap-download: 

  include $(BUILDNUMBER_FILE)

endif

UPDATE-BUILDNUMBER=echo 'INSTALLER_BUILD='`python lilypondorg.py nextbuild $(LILYPOND_VERSION)` > $(BUILDNUMBER_FILE)

$(BUILDNUMBER_FILE):
	$(UPDATE-BUILDNUMBER)

unlocked-update-buildnumber:
	$(UPDATE-BUILDNUMBER)

update-buildnumber:
	$(PYTHON) test-lily/with-lock.py --skip $(BUILDNUMBER_FILE).lock make unlocked-update-buildnumber

download:
	$(UPDATE-BUILDNUMBER)
	$(foreach p, $(PLATFORMS), $(call INVOKE_GUB_BUILDER,$(p)) download lilypond && ) true
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
	$(call BUILD,$@,lilypond)

clean:
	rm -rf $(foreach p, $(PLATFORMS), target/*$(p)* )

realclean:
	rm -rf $(foreach p, $(PLATFORMS), uploads/$(p)/* uploads/$(p)-cross/* target/*$(p)* )

TAGS: $(sources)
	etags $^

################################################################
# compilers and tools

distccd: clean-distccd cross-compilers cross-distccd native-distccd local-distcc

clean-distccd:
	rm -rf $(DISTCC_DIRS)
	mkdir -p $(DISTCC_DIRS)

local-distcc:
	chmod +x lib/distcc.py
	rm -rf target/native-distcc/bin/ target/cross-distcc/bin/
	mkdir -p target/cross-distcc/bin/ target/native-distcc/bin/
	$(foreach binary,$(foreach p,$(PLATFORMS), $(filter-out %/python-config,$(wildcard target/$(p)/system/usr/cross/bin/*))), \
		ln -s $(CWD)/lib/distcc.py target/cross-distcc/bin/$(notdir $(binary)) && ) true
	$(foreach binary, gcc g++, \
		ln -s $(CWD)/lib/distcc.py target/native-distcc/bin/$(notdir $(binary)) && ) true

cross-compilers:
	$(foreach p, $(PLATFORMS),$(call INVOKE_GUB_BUILDER, $(p)) build gcc && ) true

cross-distccd:
	-$(if $(wildcard log/$@.pid),kill `cat log/$@.pid`, true)
	rm -rf target/cross-distccd/bin/
	mkdir -p target/cross-distccd/bin/
	ln -s $(foreach p,$(PLATFORMS),$(filter-out %/python-config,$(wildcard $(CWD)/target/$(p)/system/usr/cross/bin/*))) target/cross-distccd/bin

	PATH=$(CWD)/target/local/system/usr/bin/:$(PATH) \
		DISTCCD_PATH=$(CWD)/target/cross-distccd/bin \
		distccd --daemon \
		$(addprefix --allow ,$(GUB_DISTCC_ALLOW_HOSTS)) \
		--port 3633 --pid-file $(CWD)/log/$@.pid \
		--log-file $(CWD)/log/cross-distccd.log  --log-level info

native-distccd:
	-$(if $(wildcard log/$@.pid),kill `cat log/$@.pid`, true)
	PATH=$(CWD)/target/local/system/usr/bin/:$(PATH) \
		distccd --daemon \
		$(addprefix --allow ,$(GUB_DISTCC_ALLOW_HOSTS)) \
		--port 3634 --pid-file $(CWD)/log/$@.pid \
		--log-file $(CWD)/log/$@.log  --log-level info
bootstrap:
	$(PYTHON) gub-builder.py $(LOCAL_DRIVER_OPTIONS) -p local download flex mftrace potrace fontforge \
	   guile pkg-config nsis icoutils fontconfig expat gettext \
	   distcc texinfo automake
	$(PYTHON) gub-builder.py $(LOCAL_DRIVER_OPTIONS) -p local build \
		flex mftrace potrace fontforge \
		guile pkg-config fontconfig expat icoutils glib \
		distcc texinfo automake 
	$(MAKE) cross-compilers

## TODO: switch off if mingw not in platforms.
	$(PYTHON) gub-builder.py $(LOCAL_DRIVER_OPTIONS) -p local build nsis 
	$(MAKE) download


################################################################
# docs
doc-clean:
	$(PYTHON) test-lily/with-lock.py --skip $(DOC_LOCK) $(MAKE) unlocked-doc-clean

doc-build:
	$(PYTHON) test-lily/with-lock.py --skip $(DOC_LOCK) $(MAKE) unlocked-doc-build 

NATIVE_LILY_BUILD=$(NATIVE_TARGET_DIR)/build/lilypond-$(LILYPOND_BRANCH)
NATIVE_LILY_SRC=$(NATIVE_TARGET_DIR)/src/lilypond-$(LILYPOND_BRANCH)

## no trailing slash!
NATIVE_ROOT=$(NATIVE_TARGET_DIR)/installer-$(LILYPOND_BRANCH)
DOC_LOCK=$(NATIVE_ROOT).lock

doc: doc-build

unlocked-doc-clean:
	make -C $(NATIVE_TARGET_DIR)/build/lilypond-$(LILYPOND_BRANCH) \
		DOCUMENTATION=yes web-clean

unlocked-doc-build:
	unset LILYPONDPREFIX \
	    && make -C $(NATIVE_LILY_BUILD) \
	    LILYPOND_EXTERNAL_BINARY="$(NATIVE_ROOT)/usr/bin/lilypond"\
	    PATH=$(CWD)/target/local/system/usr/bin/:$(PATH) \
	    DOCUMENTATION=yes web
	tar -C $(NATIVE_LILY_BUILD)/out-www/web-root/ \
	    -cjf $(CWD)/uploads/lilypond-$(LILYPOND_VERSION)-$(INSTALLER_BUILD).documentation.tar.bz2 . 


unlocked-doc-export:
	$(PYTHON) test-lily/rsync-lily-doc.py --recreate --output-distance \
		$(NATIVE_LILY_SRC)/buildscripts/output-distance.py $(NATIVE_LILY_BUILD)/out-www/web-root/

doc-export:
	$(PYTHON) test-lily/with-lock.py --skip $(DOC_LOCK) $(MAKE) unlocked-doc-export 
