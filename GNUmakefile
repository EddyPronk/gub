.PHONY: all default distclean download TAGS
.PHONY: cygwin darwin-ppc darwin-x86 debian freebsd4-x86 freebsd6-x86 linux-x86 mingw bootstrap-download bootstrap

default: all



## must always have one host.
GUB_DISTCC_ALLOW_HOSTS=127.0.0.1
ALL_PLATFORMS=arm cygwin darwin-ppc darwin-x86 debian freebsd-x86 freebsd-x86 linux-x86 linux-64 mingw mipsel linux-ppc
PLATFORMS=darwin-ppc darwin-x86 mingw linux-x86 linux-64 freebsd-x86 cygwin 

LILYPOND_CVS_REPODIR=downloads/lilypond.cvs
LILYPOND_CVSDIR=$(LILYPOND_CVS_REPODIR)/$(BRANCH)
LILYPOND_GITDIR=downloads/lilypond.git
LILYPOND_REPODIR=downloads/lilypond
LILYPOND_BRANCH=$(BRANCH)

# for CVS
#BRANCH=HEAD
#BRANCH=lilypond_2_8

# for GIT
BRANCH=master
# BRANCH=stable/2.10

BRANCH_FILEIFIED=$(subst /,--,$(BRANCH))

LILYPOND_LOCAL_BRANCH=$(BRANCH_FILEIFIED)-git.sv.gnu.org-lilypond.git

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


BUILD=$(call INVOKE_GUB_BUILDER,$(1)) build $(2) \
  && $(call INVOKE_INSTALLER_BUILDER,$(1)) build-all lilypond

CWD:=$(shell pwd)

DISTCC_DIRS=target/cross-distcc/bin target/cross-distccd/bin target/native-distcc/bin 

PYTHON=python
sources = GNUmakefile $(wildcard *.py specs/*.py lib/*.py)

NATIVE_TARGET_DIR=$(CWD)/target/$(BUILD_PLATFORM)

SET_LOCAL_PATH=PATH=$(CWD)/target/local/system/usr/bin:$(PATH)

LILYPOND_VERSIONS = uploads/lilypond.versions

DOC_LIMITS=ulimit -m 256000 && ulimit -d 256000 # && ulimit -v 512000 

# local.make may set the following variables:
#
#  BUILD_PLATFORM  - override the platform used for building,
#                    if ./build-platform.py should not work.
#
# it may set
#
#  GUB_CROSS_DISTCC_HOSTS - hosts with matching cross compilers
#  GUB_DISTCC_ALLOW_HOSTS - which distcc daemons may connect.
#  GUB_NATIVE_DISTCC_HOSTS - hosts with matching native compilers
#  LOCAL_GUB_BUILDER_OPTIONS - esp.: --verbose, --keep [--force-package]

BUILD_PLATFORM = $(shell $(PYTHON) build-platform.py)

-include local.make

ifeq ($(BUILD_PLATFORM),)
$(error Must define BUILD_PLATFORM)
endif 

unlocked-update-versions:
	python lib/versiondb.py --dbfile $(LILYPOND_VERSIONS) --download
	python lib/versiondb.py --dbfile uploads/fontconfig.versions --download
	python lib/versiondb.py --dbfile uploads/guile.versions --download
	python lib/versiondb.py --dbfile uploads/libtool.versions --download

update-versions:
	$(PYTHON) test-lily/with-lock.py --skip $(LILYPOND_VERSIONS).lock make unlocked-update-versions

download:
	$(foreach p, $(PLATFORMS), $(call INVOKE_GUB_BUILDER,$(p)) download lilypond && ) true
	$(MAKE) downloads/genini
	rm -f target/*/status/lilypond*
	rm -f log/lilypond-$(LILYPOND_VERSION)*.*.test.pdf

## should be last, to incorporate changed VERSION file.
	$(MAKE) update-versions

all: $(BUILD_PLATFORM) doc $(OTHER_PLATFORMS) dist-check doc-export 

native: local $(BUILD_PLATFORM)

arm:
	$(call BUILD,$@,lilypond)

docball = uploads/lilypond-$(DIST_VERSION)-$(DOC_BUILDNUMBER).documentation.tar.bz2

$(docball):
	$(MAKE) doc

# Regular cygwin stuff
cygwin: cygwin-libtool cygwin-libtool-installer doc cygwin-lilypond cygwin-lilypond-installer

cygwin-all: cygwin-libtool cygwin-libtool-installer cygwin-guile cygwin-guile-installer $(docball) cygwin-lilypond cygwin-lilypond-installer cygwin-fontconfig cygwin-fontconfig-installer

cygwin-libtool:
	rm -f uploads/cygwin/setup.ini
	$(call INVOKE_GUB_BUILDER,cygwin) --build-source build libtool

cygwin-libtool-installer:
	$(PYTHON) cygwin-packager.py libtool

cygwin-fontconfig:
	rm -f uploads/cygwin/setup.ini
	rm -rf target/cygwin/system
	$(call INVOKE_GUP, cygwin) install gcc
	$(call INVOKE_GUB_BUILDER,cygwin) --build-source build fontconfig

cygwin-fontconfig-installer:
	$(PYTHON) cygwin-packager.py fontconfig

cygwin-guile:
	$(call INVOKE_GUB_BUILDER,cygwin) --build-source build libtool guile

cygwin-guile-installer:
	$(PYTHON) cygwin-packager.py guile

cygwin-lilypond:
	$(call INVOKE_GUB_BUILDER,cygwin) --build-source build libtool guile fontconfig lilypond

cygwin-lilypond-installer:
	$(PYTHON) cygwin-packager.py --branch $(LILYPOND_LOCAL_BRANCH) lilypond

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

linux-ppc:
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

	$(SET_LOCAL_PATH) \
		DISTCCD_PATH=$(CWD)/target/cross-distccd/bin \
		distccd --daemon \
		$(addprefix --allow ,$(GUB_DISTCC_ALLOW_HOSTS)) \
		--port 3633 --pid-file $(CWD)/log/$@.pid \
		--log-file $(CWD)/log/cross-distccd.log  --log-level info

native-distccd:
	-$(if $(wildcard log/$@.pid),kill `cat log/$@.pid`, true)
	$(SET_LOCAL_PATH) \
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
		distcc texinfo automake python

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
		guile pkg-config icoutils python \
		texinfo automake gettext 


local-cross-tools:
ifneq ($(filter mingw,$(PLATFORMS)),)
	$(PYTHON) gub-builder.py $(LOCAL_DRIVER_OPTIONS) -p local build nsis 
endif

################################################################
# docs

NATIVE_ROOT=$(NATIVE_TARGET_DIR)/installer-$(LILYPOND_LOCAL_BRANCH)
DOC_LOCK=$(NATIVE_ROOT).lock

doc-clean:
	$(PYTHON) test-lily/with-lock.py --skip $(DOC_LOCK) $(MAKE) unlocked-doc-clean

doc-build:
	$(PYTHON) test-lily/with-lock.py --skip $(DOC_LOCK) $(MAKE) unlocked-doc-build unlocked-info-man-build

NATIVE_LILY_BUILD=$(NATIVE_TARGET_DIR)/build/lilypond-$(LILYPOND_LOCAL_BRANCH)
NATIVE_LILY_SRC=$(NATIVE_TARGET_DIR)/src/lilypond-$(LILYPOND_LOCAL_BRANCH)
NATIVE_BUILD_COMMITTISH=$(shell cd $(NATIVE_LILY_SRC)/ && git rev-list --max-count=1 HEAD )


DIST_VERSION=$(shell cat $(NATIVE_LILY_BUILD)/out/VERSION)
DOC_BUILDNUMBER=$(shell $(PYTHON) lib/versiondb.py --build-for $(DIST_VERSION))

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

DOC_SIGNATURE=uploads/signatures/lilypond-doc.$(NATIVE_BUILD_COMMITTISH)

unlocked-doc-build: $(DOC_SIGNATURE)

$(DOC_SIGNATURE):
	unset LILYPONDPREFIX \
	    && $(DOC_RELOCATION) \
		make -C $(NATIVE_LILY_BUILD) \
	    DOCUMENTATION=yes do-top-doc
	unset LILYPONDPREFIX \
	    && $(DOC_LIMITS) \
	    && $(DOC_RELOCATION) \
		make -C $(NATIVE_LILY_BUILD) \
	    DOCUMENTATION=yes CPU_COUNT=$(LILYPOND_WEB_CPU_COUNT) web
	$(if $(DOC_BUILDNUMBER),true,false)  ## check if we have a build number
	tar --exclude '*.signature' -C $(NATIVE_LILY_BUILD)/out-www/web-root/ \
	    -cjf $(CWD)/uploads/lilypond-$(DIST_VERSION)-$(DOC_BUILDNUMBER).documentation.tar.bz2 .
	touch $@

unlocked-info-man-build:
	unset LILYPONDPREFIX \
	    && ulimit -m 256000 \
	    && $(DOC_RELOCATION) \
		make -C $(NATIVE_LILY_BUILD)/Documentation/user \
	    DOCUMENTATION=yes out=out-www info
	$(DOC_RELOCATION) make DESTDIR=$(NATIVE_LILY_BUILD)/out-info-man \
	    -C $(NATIVE_LILY_BUILD)/Documentation/user out=www install-info

## On darwin, all our libraries have the wrong names;
## overriding with DYLD_LIBRARY_PATH doesn't work,
## as the libs in system/ are stubs.
ifneq ($(BUILD_PLATFORM),darwin-ppc)  
	## FIXME: #! guile script is barfing.
	-mkdir $(NATIVE_LILY_BUILD)/out-info-man
	touch $(NATIVE_LILY_BUILD)/scripts/out/lilypond-invoke-editor.1
	$(if $(DOC_BUILDNUMBER),true,false)  ## check if we have a build number
	$(DOC_RELOCATION) make DESTDIR=$(NATIVE_LILY_BUILD)/out-info-man \
	    -C $(NATIVE_LILY_BUILD)/ DOCUMENTATION=yes CROSS=no \
	    install-help2man
endif
	tar -C $(NATIVE_LILY_BUILD)/out-info-man/ \
	    -cjf $(CWD)/uploads/lilypond-$(DIST_VERSION)-$(DOC_BUILDNUMBER).info-man.tar.bz2 .

unlocked-doc-export:
	$(PYTHON) test-lily/rsync-lily-doc.py --recreate --output-distance \
		$(NATIVE_LILY_SRC)/buildscripts/output-distance.py $(NATIVE_LILY_BUILD)/out-www/web-root

doc-export:
	$(PYTHON) test-lily/with-lock.py --skip $(DOC_LOCK) $(MAKE) unlocked-doc-export 

unlocked-dist-check:
	$(SET_LOCAL_PATH) \
		$(PYTHON) test-lily/dist-check.py --branch $(LILYPOND_LOCAL_BRANCH) --repository $(LILYPOND_REPODIR) $(NATIVE_LILY_BUILD)
	cp $(NATIVE_LILY_BUILD)/out/lilypond-$(DIST_VERSION).tar.gz uploads/

dist-check:
	$(PYTHON) test-lily/with-lock.py --skip $(NATIVE_LILY_BUILD).lock \
		make unlocked-dist-check
