.PHONY: all default distclean download TAGS
.PHONY: cygwin darwin-ppc darwin-x86 debian freebsd4-x86 freebsd6-x86 linux-x86 mingw bootstrap-download bootstrap
.PHONY: update-buildnumber

default: all



## must always have one host.
GUB_DISTCC_ALLOW_HOSTS=127.0.0.1
ALL_PLATFORMS=arm cygwin darwin-ppc darwin-x86 debian freebsd-x86 freebsd-x86 linux-x86 linux-64 mingw mipsel
PLATFORMS=darwin-ppc darwin-x86 mingw linux-x86 linux-64 freebsd-x86 cygwin

LILYPOND_CVS_REPODIR=downloads/lilypond.cvs
LILYPOND_CVSDIR=$(LILYPOND_CVS_REPODIR)/$(BRANCH)
LILYPOND_GITDIR=downloads/lilypond.git
LILYPOND_REPODIR=downloads/lilypond
LILYPOND_BRANCH=$(BRANCH)

# for CVS
#BRANCH=HEAD

# for CVS import in GIT:
BRANCH=master
LILYPOND_LOCAL_BRANCH=master-repo.or.cz-lilypond.git
PYTHONPATH=lib/
export PYTHONPATH

OTHER_PLATFORMS=$(filter-out $(BUILD_PLATFORM), $(PLATFORMS))

INVOKE_GUB_BUILDER=$(PYTHON) gub-builder.py \
--target-platform $(1) \
--branch $(LILYPOND_BRANCH):$(LILYPOND_LOCAL_BRANCH) \
$(foreach h,$(GUB_NATIVE_DISTCC_HOSTS), --native-distcc-host $(h))\
$(foreach h,$(GUB_CROSS_DISTCC_HOSTS), --cross-distcc-host $(h))\
$(LOCAL_GUB_BUILDER_OPTIONS)

INVOKE_GUP=$(PYTHON) gup-manager.py \
--platform $(1) \
--branch $(LILYPOND_LOCAL_BRANCH)

INVOKE_INSTALLER_BUILDER=$(PYTHON) installer-builder.py \
  --target-platform $(1) \
  --branch $(LILYPOND_LOCAL_BRANCH) \

INSTALLER_BUILDNUMBER=$(shell $(PYTHON) lib/versiondb.py --build-for $(LILYPOND_VERSION))

BUILD=$(call INVOKE_GUB_BUILDER,$(1)) build $(2) \
  && $(call INVOKE_INSTALLER_BUILDER,$(1)) build-all lilypond

CWD:=$(shell pwd)

DISTCC_DIRS=target/cross-distcc/bin/ target/cross-distccd/bin/ target/native-distcc/bin/ 

PYTHON=python
sources = GNUmakefile $(wildcard *.py specs/*.py lib/*.py)

NATIVE_TARGET_DIR=$(CWD)/target/$(BUILD_PLATFORM)
VERSION_DB = uploads/versions.db

DOC_LIMITS=ulimit -m 256000 && ulimit -d 256000 # && ulimit -v 512000 

# local.make should set the following variables:
#
#  BUILD_PLATFORM  - the platform used for building.

# it may set
#
#  GUB_DISTCC_ALLOW_HOSTS - which distcc daemons may connect.
#  GUB_CROSS_DISTCC_HOSTS - hosts with matching cross compilers
#  GUB_NATIVE_DISTCC_HOSTS - hosts with matching native compilers
#

-include local.make

ifeq ($(BUILD_PLATFORM),)
$(error Must define BUILD_PLATFORM)
endif 

LILYPOND_VERSION=$(shell cat $(VERSION_FILE) || echo '0.0.0')

VERSION_FILE=VERSION-$(LILYPOND_LOCAL_BRANCH)

$(VERSION_FILE):
	$(PYTHON) gub-builder.py -p $(BUILD_PLATFORM) --inspect-output $@ --branch $(BRANCH):$(LILYPOND_LOCAL_BRANCH) inspect-version lilypond

unlocked-update-versions:
	python lib/versiondb.py --dbfile $(VERSION_DB) --download

update-versions:
	$(PYTHON) test-lily/with-lock.py --skip $(VERSION_DB).lock make unlocked-update-versions

download:
	$(foreach p, $(PLATFORMS), $(call INVOKE_GUB_BUILDER,$(p)) download lilypond && ) true
	rm -f $(VERSION_FILE)
	$(MAKE) $(VERSION_FILE)
	$(MAKE) downloads/genini
	rm -f target/*/status/lilypond*
	rm -f log/lilypond-$(LILYPOND_VERSION)*.*.test.pdf

## should be last, to incorporate changed VERSION file.
	$(MAKE) update-versions

all: $(BUILD_PLATFORM) doc $(OTHER_PLATFORMS) dist-check doc-export 

native: local $(BUILD_PLATFORM)

arm:
	$(call BUILD,$@,lilypond)


docball = uploads/lilypond-$(LILYPOND_VERSION)-$(INSTALLER_BUILDNUMBER).documentation.tar.bz2

$(docball):
	$(MAKE) doc

# Regular cygwin stuff
cygwin: cygwin-libtool cygwin-libtool-installer doc cygwin-lilypond cygwin-lilypond-installer

cygwin-all: cygwin-libtool cygwin-libtool-installer cygwin-guile cygwin-guile-installer $(docball) cygwin-lilypond cygwin-lilypond-installer cygwin-fontconfig cygwin-fontconfig-installer

cygwin-libtool:
	rm -f uploads/cygwin/setup.ini
	$(call INVOKE_GUB_BUILDER,cygwin) --build-source build libtool

cygwin-libtool-installer:
	$(PYTHON) cygwin-packager.py --build-number=3 libtool

cygwin-fontconfig:
	rm -f uploads/cygwin/setup.ini
	rm -rf target/cygwin/system
	$(call INVOKE_GUP, cygwin) install gcc
	$(call INVOKE_GUB_BUILDER,cygwin) --build-source build fontconfig

cygwin-fontconfig-installer:
	$(PYTHON) cygwin-packager.py --build-number=2 fontconfig

cygwin-guile:
	$(call INVOKE_GUB_BUILDER,cygwin) --build-source build libtool guile

cygwin-guile-installer:
	$(PYTHON) cygwin-packager.py --build-number=2 guile

cygwin-lilypond:
	$(call INVOKE_GUB_BUILDER,cygwin) --build-source build libtool guile lilypond

cygwin-lilypond-installer:
	$(PYTHON) cygwin-packager.py --branch $(LILYPOND_LOCAL_BRANCH) --build-number=2 lilypond

upload-setup-ini:
	cd uploads/cygwin && ../../downloads/genini $$(find release -mindepth 1 -maxdepth 2 -type d) > setup.ini

downloads/genini:
	wget --output-document $@ 'http://cygwin.com/cgi-bin/cvsweb.cgi/~checkout~/genini/genini?rev=1.2&content-type=text/plain&cvsroot=cygwin-apps&only_with_tag=HEAD'
	chmod +x $@

darwin-ppc:
	$(call BUILD,$@,lilypond)

darwin-x86:
	$(call BUILD,$@,lilypond)

debian:
	$(call BUILD,$@,lilypond)

freebsd4-x86:
	$(call BUILD,$@,lilypond)

freebsd6-x86:
	$(call BUILD,$@,lilypond)

freebsd-x86:
	$(call BUILD,$@,lilypond)

linux-x86:
	$(call BUILD,$@,lilypond)

linux-64:
	$(call BUILD,$@,lilypond)

mingw:
	$(call BUILD,$@,lilypond)

mipsel:
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
	$(foreach p, $(PLATFORMS),$(call INVOKE_GUB_BUILDER, $(p)) download gcc && ) true
	$(foreach p, $(PLATFORMS),$(call INVOKE_GUB_BUILDER, $(p)) build gcc && ) true

cross-distccd:
	-$(if $(wildcard log/$@.pid),kill `cat log/$@.pid`, true)
	rm -rf target/cross-distccd/bin/
	mkdir -p target/cross-distccd/bin/
	ln -s $(foreach p,$(PLATFORMS),$(filter-out %/python-config,$(wildcard $(CWD)/target/$(p)/system/usr/cross/bin/*))) target/cross-distccd/bin

	PATH=$(CWD)/target/local/system/usr/bin:$(PATH) \
		DISTCCD_PATH=$(CWD)/target/cross-distccd/bin \
		distccd --daemon \
		$(addprefix --allow ,$(GUB_DISTCC_ALLOW_HOSTS)) \
		--port 3633 --pid-file $(CWD)/log/$@.pid \
		--log-file $(CWD)/log/cross-distccd.log  --log-level info

native-distccd:
	-$(if $(wildcard log/$@.pid),kill `cat log/$@.pid`, true)
	PATH=$(CWD)/target/local/system/usr/bin:$(PATH) \
		distccd --daemon \
		$(addprefix --allow ,$(GUB_DISTCC_ALLOW_HOSTS)) \
		--port 3634 --pid-file $(CWD)/log/$@.pid \
		--log-file $(CWD)/log/$@.log  --log-level info

bootstrap: bootstrap-git download-local local cross-compilers local-cross-tools download 

bootstrap-git:
	$(PYTHON) gub-builder.py $(LOCAL_GUB_BUILDER_OPTIONS) -p local download git
	$(PYTHON) gub-builder.py $(LOCAL_GUB_BUILDER_OPTIONS) -p local build git

download-local:
	$(PYTHON) gub-builder.py $(LOCAL_GUB_BUILDER_OPTIONS) -p local download \
		git flex mftrace potrace fontforge \
		guile pkg-config nsis icoutils expat gettext \
		distcc texinfo automake

###
# document why this is in the bootstrap

# -guile: bootstrap guile
# -gettext: AM_GNU_GETTEXT
# -mftrace, fontforge, potrace: lilypond
# -texinfo: need 4.8 for lily
# -automake: prevent version confusion
# -pkg-config: nonstandard (eg. MacOS)
# -icoutils: lilypond mingw icons
# -distcc: nonstandard (eg. MacOS)
# -freetype: for bootstrapping fontconfig
#

local:
	$(PYTHON) gub-builder.py $(LOCAL_GUB_BUILDER_OPTIONS) -p local build \
		git flex mftrace potrace fontforge freetype \
		guile pkg-config icoutils \
		distcc texinfo automake gettext 


local-cross-tools:
ifneq ($(filter mingw,$(PLATFORMS)),)
	$(PYTHON) gub-builder.py $(LOCAL_DRIVER_OPTIONS) -p local build nsis 
endif

################################################################
# docs
doc-clean:
	$(PYTHON) test-lily/with-lock.py --skip $(DOC_LOCK) $(MAKE) unlocked-doc-clean

doc-build:
	$(PYTHON) test-lily/with-lock.py --skip $(DOC_LOCK) $(MAKE) unlocked-doc-build unlocked-info-man-build

NATIVE_LILY_BUILD=$(NATIVE_TARGET_DIR)/build/lilypond-$(LILYPOND_LOCAL_BRANCH)
NATIVE_LILY_SRC=$(NATIVE_TARGET_DIR)/src/lilypond-$(LILYPOND_LOCAL_BRANCH)

NATIVE_ROOT=$(NATIVE_TARGET_DIR)/installer-$(LILYPOND_LOCAL_BRANCH)

DOC_LOCK=$(NATIVE_ROOT).lock

doc: native doc-build

unlocked-doc-clean:
	make -C $(NATIVE_TARGET_DIR)/build/lilypond-$(LILYPOND_LOCAL_BRANCH) \
		DOCUMENTATION=yes web-clean

DOC_RELOCATION = \
    LILYPOND_EXTERNAL_BINARY="$(NATIVE_ROOT)/usr/bin/lilypond" \
    PATH=$(CWD)/target/local/system/usr/bin:$(NATIVE_ROOT)/usr/bin:$$PATH \
    GS_LIB=$(wildcard $(NATIVE_ROOT)/usr/share/ghostscript/*/lib) \
    LD_LIBRARY_PATH=$(NATIVE_ROOT)/usr/lib:$$LD_LIBRARY_PATH
    MALLOC_CHECK_=2 \

unlocked-doc-build:
	unset LILYPONDPREFIX \
	    && $(DOC_RELOCATION) \
		make -C $(NATIVE_LILY_BUILD) \
	    DOCUMENTATION=yes do-top-doc
	unset LILYPONDPREFIX \
	    && $(DOC_LIMITS) \
	    && $(DOC_RELOCATION) \
		make -C $(NATIVE_LILY_BUILD) \
	    DOCUMENTATION=yes web
	tar --exclude '*.signature' -C $(NATIVE_LILY_BUILD)/out-www/web-root/ \
	    -cjf $(CWD)/uploads/lilypond-$(LILYPOND_VERSION)-$(INSTALLER_BUILDNUMBER).documentation.tar.bz2 . 

unlocked-info-man-build:
	unset LILYPONDPREFIX \
	    && ulimit -m 256000 \
	    && $(DOC_RELOCATION) \
		make -C $(NATIVE_LILY_BUILD)/Documentation/user \
	    DOCUMENTATION=yes out=out-www info
	$(DOC_RELOCATION) make DESTDIR=$(NATIVE_LILY_BUILD)/out-info-man \
	    -C $(NATIVE_LILY_BUILD)/Documentation/user out=www install-info
	$(DOC_RELOCATION) make DESTDIR=$(NATIVE_LILY_BUILD)/out-info-man \
	    -C $(NATIVE_LILY_BUILD)/ DOCUMENTATION=yes CROSS=no \
	    install-help2man
	tar -C $(NATIVE_LILY_BUILD)/out-info-man/ \
	    -cjf $(CWD)/uploads/lilypond-$(LILYPOND_VERSION)-$(INSTALLER_BUILDNUMBER).info-man.tar.bz2 .

unlocked-doc-export:
	$(PYTHON) test-lily/rsync-lily-doc.py --recreate --output-distance \
		$(NATIVE_LILY_SRC)/buildscripts/output-distance.py $(NATIVE_LILY_BUILD)/out-www/web-root

doc-export:
	$(PYTHON) test-lily/with-lock.py --skip $(DOC_LOCK) $(MAKE) unlocked-doc-export 

unlocked-dist-check:
	$(PYTHON) test-lily/dist-check.py --branch $(LILYPOND_LOCAL_BRANCH) --repository $(LILYPOND_REPODIR) $(NATIVE_LILY_BUILD)
	rm -f uploads/lilypond-$(LILYPOND_VERSION).tar.gz
	ln $(NATIVE_LILY_BUILD)/out/lilypond-$(LILYPOND_VERSION).tar.gz uploads/

dist-check:
	$(PYTHON) test-lily/with-lock.py --skip $(NATIVE_LILY_BUILD).lock \
		make unlocked-dist-check
