# -*-Makefile-*-
.PHONY: all default distclean download TAGS
.PHONY: cygwin debian debian-arm
.PHONY: darwin-ppc darwin-x86 freebsd4-x86 freebsd6-x86 linux-x86 mingw
.PHONY: bootstrap-download bootstrap
.PHONY: unlocked-update-versions update-versions download print-success
.PHONY: cygwin-libtool cygwin-libtool-installer cygwin-fontconfig
.PHONY: cygwin-fontconfig-installer cygwin-guile cygwin-guile-installer
.PHONY: cygwin-lilypond cygwin-lilypond-installer upload-setup-ini darwin-ppc
.PHONY: debian linux-ppc mingw mipsel clean realclean clean-distccd
.PHONY: local-distcc cross-compilers cross-distccd native-distccd
.PHONY: bootstrap-git download-local local local-cross-tools doc-clean
.PHONY: unlocked-doc-clean unlocked-doc-build unlocked-info-man-build
.PHONY: unlocked-doc-export doc-export unlocked-dist-check dist-check

default: all

PACKAGE = lilypond

ALL_PLATFORMS=cygwin darwin-ppc darwin-x86 debian debian-arm freebsd-x86 linux-x86 linux-64 mingw mipsel linux-ppc
PLATFORMS=darwin-ppc darwin-x86 mingw linux-x86 linux-64 linux-ppc freebsd-x86 cygwin

LILYPOND_CVS_REPODIR=downloads/lilypond.cvs
LILYPOND_GITDIR=downloads/lilypond.git
LILYPOND_REPODIR=downloads/lilypond

# for GIT
LILYPOND_BRANCH=master
# LILYPOND_BRANCH=stable/2.10

MAKE += -f lilypond.make
LILYPOND_BRANCH_FILEIFIED=$(subst /,--,$(LILYPOND_BRANCH))

LILYPOND_LOCAL_BRANCH=$(LILYPOND_BRANCH_FILEIFIED)-git.sv.gnu.org-lilypond.git

GUB_BUILDER_OPTIONS =\
 --branch lilypond=$(LILYPOND_BRANCH):$(LILYPOND_LOCAL_BRANCH)

GUP_OPTIONS =\
 --branch guile=branch_release-1-8-repo.or.cz-guile.git\
 --branch lilypond=$(LILYPOND_LOCAL_BRANCH)

INSTALLER_BUILDER_OPTIONS =\
 --branch guile=branch_release-1-8-repo.or.cz-guile.git \
 --branch lilypond=$(LILYPOND_LOCAL_BRANCH)

include gub.make

NATIVE_TARGET_DIR=$(CWD)/target/$(BUILD_PLATFORM)

SET_LOCAL_PATH=PATH=$(CWD)/target/local/usr/bin:$(PATH)

LILYPOND_VERSIONS = uploads/lilypond.versions

DOC_LIMITS=ulimit -m 256000 && ulimit -d 256000 && ulimit -v 384000

include compilers.make

################

unlocked-update-versions:
	python lib/versiondb.py --dbfile $(LILYPOND_VERSIONS) --download
	python lib/versiondb.py --dbfile uploads/fontconfig.versions --download
	python lib/versiondb.py --dbfile uploads/guile.versions --download
	python lib/versiondb.py --dbfile uploads/libtool.versions --download

update-versions:
	$(PYTHON) lib/with-lock.py --skip $(LILYPOND_VERSIONS).lock $(MAKE) unlocked-update-versions

download:
	$(foreach p, $(PLATFORMS), $(call INVOKE_GUB_BUILDER,$(p)) --stage=download lilypond && ) true
	$(MAKE) downloads/genini
	rm -f target/*/status/lilypond*
	rm -f log/lilypond-$(LILYPOND_VERSION)*.*.test.pdf

## should be last, to incorporate changed VERSION file.
	$(MAKE) update-versions

all: native dist-check doc-build doc-export $(OTHER_PLATFORMS) print-success

platforms: $(PLATFORMS)

print-success:
	python test-lily/upload.py --branch $(LILYPOND_LOCAL_BRANCH)
	@echo ""
	@echo "To upload, run "
	@echo
	@echo "        python test-lily/upload.py --branch $(LILYPOND_LOCAL_BRANCH) --execute"
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
	$(call INVOKE_GUB_BUILDER,cygwin) --build-source libtool

cygwin-libtool-installer:
	$(CYGWIN_PACKAGER) libtool

cygwin-fontconfig:
	rm -f uploads/cygwin/setup.ini
	rm -rf target/cygwin/
	$(call INVOKE_GUP, cygwin) install gcc
	$(call INVOKE_GUB_BUILDER,cygwin) --build-source fontconfig

cygwin-fontconfig-installer:
	$(CYGWIN_PACKAGER) fontconfig

cygwin-guile:
	$(call INVOKE_GUB_BUILDER,cygwin) --build-source libtool guile

cygwin-guile-installer:
	$(CYGWIN_PACKAGER) guile

cygwin-lilypond:
	$(call INVOKE_GUB_BUILDER,cygwin) --build-source libtool guile fontconfig lilypond

cygwin-lilypond-installer:
	$(CYGWIN_PACKAGER) --branch lilypond=$(LILYPOND_LOCAL_BRANCH) lilypond

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
 texinfo

ifneq ($(BUILD_PLATFORM),linux-64)
locals += nsis
endif

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

download-local:
	$(GUB_BUILDER) $(LOCAL_GUB_BUILDER_OPTIONS) \
		-p local --stage=download \
		$(locals)

local:
	cd librestrict && make -f GNUmakefile
	$(GUB_BUILDER) $(LOCAL_GUB_BUILDER_OPTIONS) -p local \
		$(locals)


################################################################
# docs

NATIVE_ROOT=$(NATIVE_TARGET_DIR)/gubfiles/installer-lilypond-$(LILYPOND_LOCAL_BRANCH)
DOC_LOCK=$(NATIVE_ROOT).lock



NATIVE_LILY_BUILD=$(NATIVE_TARGET_DIR)/gubfiles/build/lilypond-$(LILYPOND_LOCAL_BRANCH)
NATIVE_LILY_SRC=$(NATIVE_TARGET_DIR)/gubfiles/src/lilypond-$(LILYPOND_LOCAL_BRANCH)
NATIVE_BUILD_COMMITTISH=$(shell cat downloads/lilypond.git/refs/heads/$(LILYPOND_LOCAL_BRANCH))

DIST_VERSION=$(shell cat $(NATIVE_LILY_BUILD)/out/VERSION)
DOC_BUILDNUMBER=$(shell $(PYTHON) lib/versiondb.py --build-for $(DIST_VERSION))

DOC_RELOCATION = \
    LILYPOND_EXTERNAL_BINARY="$(NATIVE_ROOT)/usr/bin/lilypond" \
    PATH=$(CWD)/target/local/usr/bin:$(NATIVE_ROOT)/usr/bin:$$PATH \
    GS_LIB=$(wildcard $(NATIVE_ROOT)/usr/share/ghostscript/*/lib) \
    MALLOC_CHECK_=2 \
    LD_LIBRARY_PATH=$(NATIVE_ROOT)/usr/lib

SIGNATURE_FUNCTION=uploads/signatures/$(1).$(NATIVE_BUILD_COMMITTISH)

doc: native doc-build

doc-clean:
	$(PYTHON) lib/with-lock.py --skip $(DOC_LOCK) $(MAKE) unlocked-doc-clean

doc-build:
	$(PYTHON) lib/with-lock.py --skip $(DOC_LOCK) $(MAKE) cached-doc-build

unlocked-doc-clean:
	make -C $(NATIVE_TARGET_DIR)/gubfiles/build/lilypond-$(LILYPOND_LOCAL_BRANCH) \
		DOCUMENTATION=yes web-clean
	rm -f $(call SIGNATURE_FUNCTION,cached-doc-build)
	rm -f $(call SIGNATURE_FUNCTION,cached-doc-export)

cached-doc-build cached-dist-check cached-doc-export:
	-mkdir uploads/signatures/
	if test ! -f  $(call SIGNATURE_FUNCTION,$@) ; then \
		$(MAKE) $(subst cached,unlocked,$@) \
		&& touch $(call SIGNATURE_FUNCTION,$@) ; fi

unlocked-doc-build:
	$(GUP_MANAGER) -p $(BUILD_PLATFORM) remove lilypond

	## force update of srcdir.
	$(GUB_BUILDER) --branch lilypond=$(LILYPOND_BRANCH):$(LILYPOND_LOCAL_BRANCH) \
		 -p $(BUILD_PLATFORM) --stage untar lilypond

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
		--version-file $(NATIVE_LILY_BUILD)/out/VERSION \
		--output-distance \
		$(NATIVE_LILY_SRC)/buildscripts/output-distance.py $(NATIVE_LILY_BUILD)/out-www/online-root

doc-export:
	$(PYTHON) lib/with-lock.py --skip $(DOC_LOCK) $(MAKE) cached-doc-export

unlocked-dist-check:
	$(SET_LOCAL_PATH) \
		$(PYTHON) test-lily/dist-check.py --branch $(LILYPOND_LOCAL_BRANCH) --repository $(LILYPOND_REPODIR) $(NATIVE_LILY_BUILD)
	cp $(NATIVE_LILY_BUILD)/out/lilypond-$(DIST_VERSION).tar.gz uploads/

dist-check:
	$(PYTHON) lib/with-lock.py --skip $(NATIVE_LILY_BUILD).lock \
		$(MAKE) cached-dist-check
