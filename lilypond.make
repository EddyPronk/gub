# -*-Makefile-*-
.PHONY: all default distclean download TAGS
.PHONY: cygwin debian debian-arm
.PHONY: darwin-ppc darwin-x86 freebsd4-x86 freebsd6-x86 linux-x86 mingw
.PHONY: bootstrap-download bootstrap
.PHONY: unlocked-update-versions update-versions download print-success
.PHONY: debian linux-ppc mingw mipsel clean realclean clean-distccd
.PHONY: local-distcc cross-compilers cross-distccd native-distccd
.PHONY: bootstrap-git download-local local local-cross-tools doc-clean
.PHONY: unlocked-doc-clean unlocked-doc-build unlocked-info-man-build
.PHONY: unlocked-doc-export doc-export unlocked-dist-check dist-check

.PHONY: cygwin-libtool cygwin-libtool-installer cygwin-fontconfig
.PHONY: cygwin-freetype2 cygwin-freetype2-installer
.PHONY: cygwin-fontconfig-installer cygwin-guile cygwin-guile-installer
.PHONY: cygwin-lilypond cygwin-lilypond-installer upload-setup-ini darwin-ppc

default: all

PACKAGE = lilypond

ALL_PLATFORMS=linux-x86 darwin-ppc darwin-x86 debian debian-arm freebsd-64 freebsd-x86 linux-64 mingw debian-mipsel linux-ppc
PLATFORMS=linux-x86 linux-64 linux-ppc freebsd-x86 freebsd-64

# XBUILD_PLATFORM: leave checks in place for now:
# we need 32 bit compatibility libs and linux-x86 built for this to work

ifneq ($(XBUILD_PLATFORM),linux-64)
# odcctools do not build with 64 bit compiler
PLATFORMS+=darwin-ppc darwin-x86
endif

ifneq ($(XBUILD_PLATFORM),linux-64)
# nsis does not build with 64 bit compiler
PLATFORMS+=mingw
endif


## want cygwin to be the last, because it is not a core lilypond platform. 
ALL_PLATFORMS += cygwin
PLATFORMS += cygwin


LILYPOND_CVS_REPODIR=downloads/lilypond.cvs
LILYPOND_GITDIR=downloads/lilypond.git
LILYPOND_REPODIR=downloads/lilypond

# for GIT
LILYPOND_BRANCH=master
# LILYPOND_BRANCH=stable/2.10

MAKE += -f lilypond.make
LILYPOND_BRANCH_FILEIFIED=$(subst /,--,$(LILYPOND_BRANCH))

LILYPOND_LOCAL_BRANCH=$(LILYPOND_BRANCH_FILEIFIED)-git.sv.gnu.org-lilypond.git

# FIXME: this is duplicated and must match actual info in guile.py
GUILE_LOCAL_BRANCH=branch_release-1-8-lilypond.org-vc-guile.git
GUILE_LOCAL_BRANCH=branch_release-1-8-repo.or.cz-guile.git

GUB_OPTIONS =\
 --branch=lilypond=$(LILYPOND_BRANCH):$(LILYPOND_LOCAL_BRANCH)

GPKG_OPTIONS =\
 $(if $(GUILE_LOCAL_BRANCH), --branch=guile=$(GUILE_LOCAL_BRANCH),)\
 --branch=lilypond=$(LILYPOND_LOCAL_BRANCH)

INSTALLER_BUILDER_OPTIONS =\
 $(if $(GUILE_LOCAL_BRANCH), --branch=guile=$(GUILE_LOCAL_BRANCH),)\
 --branch=lilypond=$(LILYPOND_LOCAL_BRANCH)

include gub.make

NATIVE_TARGET_DIR=$(CWD)/target/$(BUILD_PLATFORM)

SET_LOCAL_PATH=PATH=$(CWD)/target/local/usr/bin:$(PATH)

LILYPOND_VERSIONS = uploads/lilypond.versions

DOC_LIMITS=ulimit -m 256000 && ulimit -d 256000 && ulimit -v 384000

include compilers.make

################

unlocked-update-versions:
	python gub/versiondb.py --dbfile=$(LILYPOND_VERSIONS) --download  --platforms="$(PLATFORMS)"
	python gub/versiondb.py --dbfile=uploads/freetype2.versions --download  --platforms="cygwin"
	python gub/versiondb.py --dbfile=uploads/fontconfig.versions --download  --platforms="cygwin"
	python gub/versiondb.py --dbfile=uploads/guile.versions --download --platforms="cygwin"
	python gub/versiondb.py --dbfile=uploads/libtool.versions --download --platforms="cygwin"
	python gub/versiondb.py --dbfile=uploads/noweb.versions --download --platforms="cygwin"

update-versions:
	$(PYTHON) gub/with-lock.py --skip $(LILYPOND_VERSIONS).lock $(MAKE) unlocked-update-versions

download:
	$(foreach p, $(PLATFORMS), $(call INVOKE_GUB,$(p)) --online --stage=download lilypond && ) true
	$(MAKE) downloads/genini
	rm -f target/*/status/lilypond*
	rm -f log/lilypond-$(LILYPOND_VERSION)*.*.test.pdf

## should be last, to incorporate changed VERSION file.
	$(MAKE) update-versions

all: native dist-check doc-build test-output doc-export $(OTHER_PLATFORMS) print-success

platforms: $(PLATFORMS)

print-success:
	python test-lily/upload.py --branch=$(LILYPOND_LOCAL_BRANCH)
	@echo ""
	@echo "To upload, run "
	@echo
	@echo "        python test-lily/upload.py --branch=$(LILYPOND_LOCAL_BRANCH) --execute"
	@echo

native: local $(BUILD_PLATFORM)

debian-arm:
	$(call BUILD,$@,lilypond)

docball = uploads/lilypond-$(DIST_VERSION)-$(DOC_BUILDNUMBER).documentation.tar.bz2

$(docball):
	$(MAKE) doc

# Regular cygwin stuff
cygwin: cygwin-libtool cygwin-libtool-installer doc cygwin-lilypond cygwin-lilypond-installer

cygwin-all: cygwin-libtool cygwin-libtool-installer cygwin-guile cygwin-guile-installer $(docball) cygwin-lilypond cygwin-lilypond-installer cygwin-fontconfig cygwin-fontconfig-installer

cygwin-libtool:
	rm -f uploads/cygwin/setup.ini
	$(call INVOKE_GUB,cygwin) --build-source libtool

cygwin-libtool-installer:
	$(CYGWIN_PACKAGER) libtool

cygwin-freetype2:
	# when forcing a source build we remove everything,
	# because freetype by default comes from cygwin as a binary
	rm -f uploads/cygwin/setup.ini
	rm -rf target/cygwin/
	$(call INVOKE_GUP, cygwin) install cross/gcc
#	$(call INVOKE_GUB,cygwin) freetype-config
	$(call INVOKE_GUB,cygwin) --build-source freetype2

cygwin-freetype2-installer:
	$(CYGWIN_PACKAGER) freetype2

cygwin-fontconfig:
	# when forcing a source build we remove everything,
	# because fontconfig by default comes from cygwin as a binary
	rm -f uploads/cygwin/setup.ini
	rm -rf target/cygwin/
	$(call INVOKE_GUP, cygwin) install cross/gcc
	$(call INVOKE_GUB,cygwin) --build-source fontconfig

cygwin-fontconfig-installer:
	$(CYGWIN_PACKAGER) fontconfig

cygwin-guile:
	$(call INVOKE_GUB,cygwin) --build-source libtool guile

cygwin-guile-installer:
	$(CYGWIN_PACKAGER) guile

cygwin-lilypond:
	$(call INVOKE_GUB,cygwin) --build-source libtool guile fontconfig lilypond

cygwin-lilypond-installer:
	$(CYGWIN_PACKAGER) --branch=lilypond=$(LILYPOND_LOCAL_BRANCH) lilypond

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

freebsd-64:
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


################################################################
# compilers and tools

locals =\
 automake\
 distcc\
 expat\
 flex\
 fontforge\
 freetype\
 gettext\
 git\
 guile\
 icoutils\
 mftrace\
 netpbm\
 pkg-config\
 potrace\
 python\
 imagemagick \
 texinfo

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
# -imagemagick: for lilypond web site
# -netpbm: website
# -python: bootstrap for python x-compile
# -icoutils: icon build for mingw
download-local:
ifneq ($(BUILD_PLATFORM),linux-64)
	$(GUB) $(LOCAL_GUB_OPTIONS) --platform=local --stage=download $(locals) nsis
else
# ugh, can only download nsis after cross-compilers...
	$(GUB) $(LOCAL_GUB_OPTIONS) --platform=local --stage=download $(locals)
endif

local:
	cd librestrict && make -f GNUmakefile
	$(GUB) $(LOCAL_GUB_OPTIONS) --platform=local $(locals)
# local-cross-tools depend on cross-compilers, see compilers.make.
# We need linux-x86 and mingw before nsis can be build
#	$(MAKE) local-cross-tools

################################################################
# docs

NATIVE_ROOT=$(NATIVE_TARGET_DIR)/installer-lilypond-$(LILYPOND_LOCAL_BRANCH)
DOC_LOCK=$(NATIVE_ROOT).lock
TEST_LOCK=$(NATIVE_ROOT).lock

NATIVE_LILY_BUILD=$(NATIVE_TARGET_DIR)/build/lilypond-$(LILYPOND_LOCAL_BRANCH)
NATIVE_LILY_SRC=$(NATIVE_TARGET_DIR)/src/lilypond-$(LILYPOND_LOCAL_BRANCH)
NATIVE_BUILD_COMMITTISH=$(shell cat downloads/lilypond.git/refs/heads/$(LILYPOND_LOCAL_BRANCH))

DIST_VERSION=$(shell cat $(NATIVE_LILY_BUILD)/out/VERSION)
DOC_BUILDNUMBER=$(shell $(PYTHON) gub/versiondb.py --build-for=$(DIST_VERSION))

DOC_RELOCATION = \
    LILYPOND_EXTERNAL_BINARY="$(NATIVE_ROOT)/usr/bin/lilypond" \
    PATH=$(CWD)/target/local/root/usr/bin:$(NATIVE_ROOT)/usr/bin:$$PATH \
    GS_LIB=$(wildcard $(NATIVE_ROOT)/usr/share/ghostscript/*/lib) \
    MALLOC_CHECK_=2 \
    LD_LIBRARY_PATH=$(NATIVE_ROOT)/usr/lib

SIGNATURE_FUNCTION=uploads/signatures/$(1).$(NATIVE_BUILD_COMMITTISH)


doc: native doc-build

doc-clean:
	$(PYTHON) gub/with-lock.py --skip $(DOC_LOCK) $(MAKE) unlocked-doc-clean

doc-build:
	$(PYTHON) gub/with-lock.py --skip $(DOC_LOCK) $(MAKE) cached-doc-build

test-output:
	$(PYTHON) gub/with-lock.py --skip $(TEST_LOCK) $(MAKE) cached-test-output

test-clean:
	$(PYTHON) gub/with-lock.py --skip $(TEST_LOCK) $(MAKE) unlocked-test-clean

unlocked-doc-clean:
	make -C $(NATIVE_TARGET_DIR)/build/lilypond-$(LILYPOND_LOCAL_BRANCH) \
		DOCUMENTATION=yes web-clean
	rm -f $(call SIGNATURE_FUNCTION,cached-doc-build)
	rm -f $(call SIGNATURE_FUNCTION,cached-doc-export)

unlocked-test-clean:
	make -C $(NATIVE_TARGET_DIR)/build/lilypond-$(LILYPOND_LOCAL_BRANCH) \
		DOCUMENTATION=yes test-clean
	rm -f $(call SIGNATURE_FUNCTION,cached-test-output)

cached-test-output cached-doc-build cached-dist-check cached-doc-export cached-info-man-build cached-test-export:
	-mkdir uploads/signatures/
	if test ! -f  $(call SIGNATURE_FUNCTION,$@) ; then \
		$(MAKE) $(subst cached,unlocked,$@) \
		&& touch $(call SIGNATURE_FUNCTION,$@) ; fi
unlocked-test-output:
	cd $(NATIVE_LILY_BUILD) && $(DOC_RELOCATION) \
		make CPU_COUNT=$(LILYPOND_WEB_CPU_COUNT)  test
	tar -C $(NATIVE_LILY_BUILD)/ \
	    -cjf $(CWD)/uploads/lilypond-$(DIST_VERSION)-$(DOC_BUILDNUMBER).test-output.tar.bz2 input/regression/out-test/

unlocked-doc-build:
	$(GPKG) --platform=$(BUILD_PLATFORM) remove lilypond

	## force update of srcdir.
	$(GUB) --branch=lilypond=$(LILYPOND_BRANCH):$(LILYPOND_LOCAL_BRANCH) \
		 --platform=$(BUILD_PLATFORM) --stage=untar lilypond

	unset LILYPONDPREFIX LILYPOND_DATADIR \
	    && $(DOC_RELOCATION) \
		make -C $(NATIVE_LILY_BUILD) \
	    DOCUMENTATION=yes do-top-doc
	unset LILYPONDPREFIX LILYPOND_DATADIR \
	    && $(DOC_LIMITS) \
	    && $(DOC_RELOCATION) \
		make -C $(NATIVE_LILY_BUILD) \
	    DOCUMENTATION=yes \
	    WEB_TARGETS="offline online" \
	    CPU_COUNT=$(LILYPOND_WEB_CPU_COUNT) web
	$(if $(DOC_BUILDNUMBER),true,false)  ## check if we have a build number
	$(if $(DIST_VERSION),true,false)  ## check if we have a version number
	tar --exclude '*.signature' -C $(NATIVE_LILY_BUILD)/out-www/offline-root \
	    -cjf $(CWD)/uploads/lilypond-$(DIST_VERSION)-$(DOC_BUILDNUMBER).documentation.tar.bz2 .
	tar --exclude '*.signature' -C $(NATIVE_LILY_BUILD)/out-www/online-root \
	    -cjf $(CWD)/uploads/lilypond-$(DIST_VERSION)-$(DOC_BUILDNUMBER).webdoc.tar.bz2 .

unlocked-info-man-build:
	unset LILYPONDPREFIX LILYPOND_DATADIR \
	    && ulimit -m 256000 \
	    && $(DOC_RELOCATION) \
		make -C $(NATIVE_LILY_BUILD)/Documentation/user \
	    DOCUMENTATION=yes out=www info
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
	PYTHONPATH=$(NATIVE_LILY_BUILD)/python/out \
	$(PYTHON) test-lily/rsync-lily-doc.py --recreate \
		--version-file=$(NATIVE_LILY_BUILD)/out/VERSION \
		--output-distance=$(NATIVE_LILY_SRC)/buildscripts/output-distance.py $(NATIVE_LILY_BUILD)/out-www/online-root
	$(PYTHON) test-lily/rsync-lily-doc.py --recreate \
		--version-file=$(NATIVE_LILY_BUILD)/out/VERSION \
		--unpack-dir=uploads/localdoc/ \
		--output-distance=$(NATIVE_LILY_SRC)/buildscripts/output-distance.py $(NATIVE_LILY_BUILD)/out-www/offline-root

unlocked-test-export:
	PYTHONPATH=$(NATIVE_LILY_BUILD)/python/out \
	$(PYTHON) test-lily/rsync-test.py \
		--version-file=$(NATIVE_LILY_BUILD)/out/VERSION \
		--output-distance=$(NATIVE_LILY_SRC)/buildscripts/output-distance.py \
		--test-dir=uploads/webtest

doc-export:
	$(PYTHON) gub/with-lock.py --skip $(DOC_LOCK) $(MAKE) cached-doc-export

test-export:
	$(PYTHON) gub/with-lock.py --skip $(DOC_LOCK) $(MAKE) cached-test-export

unlocked-dist-check:
	$(SET_LOCAL_PATH)\
		$(PYTHON) test-lily/dist-check.py\
		--branch=$(LILYPOND_LOCAL_BRANCH)\
		--repository=$(LILYPOND_REPODIR) $(NATIVE_LILY_BUILD)
	cp $(NATIVE_LILY_BUILD)/out/lilypond-$(DIST_VERSION).tar.gz uploads

dist-check:
	$(PYTHON) gub/with-lock.py --skip $(NATIVE_LILY_BUILD).lock \
		$(MAKE) cached-dist-check
