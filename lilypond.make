# -*-Makefile-*-
.PHONY: all default distclean rest print-success
.PHONY: clean realclean
.PHONY: test test-output test-clean
.PHONY: update-versions unlocked-update-versions
.PHONY: doc doc-clean doc-export unlocked-doc-clean unlocked-doc-export
.PHONY: dist-check unlocked-dist-check

default: all

LILYPOND_BRANCH=master
# LILYPOND_BRANCH=stable/2.10
LILYPOND_REPO_URL=git://git.sv.gnu.org/lilypond.git

ALL_PLATFORMS=linux-x86 darwin-ppc darwin-x86 mingw linux-64 debian debian-arm freebsd-64 freebsd-x86 debian-mipsel linux-ppc
ALL_PLATFORMS += cygwin

PLATFORMS=linux-x86
PLATFORMS+=darwin-ppc darwin-x86
PLATFORMS+=mingw
PLATFORMS+=linux-64
PLATFORMS+=linux-ppc
PLATFORMS+=freebsd-x86 freebsd-64
# Put cygwin last, because it is not a core lilypond platform. 
#PLATFORMS += cygwin

ifeq ($(LILYPOND_BRANCH),stable/2.10)
$(error backportme:\
0d9ce36... When LINK_GXX_STATICALLY=yes, use CC (ie, [*-*-]gcc) for linking.  Fixes --enable-static-c++.\
841ee1b... PYTHON-CONFIG: also strip -m* and =.  Thanks Werner!\
f9e5179... Append /../lib to default rpath.\
fc158e0... Add --enable-rpath feature, defaulting to $ORIGIN/../lib. Default off.\
23e401a... Clean-out some junk flags from python-config.  Fixes stray g++ warnings.\
)
endif

# derived info
LILYPOND_SOURCE_URL=$(LILYPOND_REPO_URL)?branch=$(LILYPOND_BRANCH)
LILYPOND_DIRRED_BRANCH=$(shell $(PYTHON) gub/repository.py --branch-dir '$(LILYPOND_SOURCE_URL)')
LILYPOND_FLATTENED_BRANCH=$(shell $(PYTHON) gub/repository.py --full-branch-name '$(LILYPOND_SOURCE_URL)')
BUILD_PACKAGE='$(LILYPOND_SOURCE_URL)'
INSTALL_PACKAGE = lilypond

MAKE += -f lilypond.make

# FIXME: this is duplicated and must match actual info in guile.py

GUB_OPTIONS =

GPKG_OPTIONS =\
 $(if $(GUILE_LOCAL_BRANCH), --branch=guile=$(GUILE_LOCAL_BRANCH),)\
 --branch=lilypond=$(LILYPOND_BRANCH)

INSTALLER_BUILDER_OPTIONS =\
 $(if $(GUILE_LOCAL_BRANCH), --branch=guile=$(GUILE_LOCAL_BRANCH),)\
 --branch=lilypond=$(LILYPOND_FLATTENED_BRANCH)

include gub.make

NATIVE_TARGET_DIR=$(CWD)/target/$(BUILD_PLATFORM)

#FIXME: yet another copy of gub/settings.py
SET_LOCAL_PATH=PATH=$(CWD)/target/local/root/usr/bin:$(PATH)

LILYPOND_VERSIONS = uploads/lilypond.versions

include compilers.make

################

unlocked-update-versions:
	python gub/versiondb.py --dbfile=$(LILYPOND_VERSIONS) --download --platforms="$(PLATFORMS)"

ifneq ($(findstring cygwin,$(PLATFORMS)),)
# this is downloading the same info 5 times. Can we do this more efficiently?
	python gub/versiondb.py --no-sources  --dbfile=uploads/freetype2.versions --download  --platforms="cygwin"
	python gub/versiondb.py --no-sources --dbfile=uploads/fontconfig.versions --download  --platforms="cygwin"
	python gub/versiondb.py --no-sources  --dbfile=uploads/guile.versions --download --platforms="cygwin"
	python gub/versiondb.py --no-sources  --dbfile=uploads/libtool.versions --download --platforms="cygwin"
	python gub/versiondb.py --no-sources  --dbfile=uploads/noweb.versions --download --platforms="cygwin"
endif

update-versions:
	$(PYTHON) gub/with-lock.py --skip $(LILYPOND_VERSIONS).lock $(MAKE) unlocked-update-versions

download-cygwin:
	$(MAKE) downloads/genini
	rm -f target/*/status/lilypond*
	rm -f log/lilypond-$(LILYPOND_VERSION)*.*.test.pdf

## should be last, to incorporate changed VERSION file.
	$(MAKE) update-versions

all: packages rest

rest: installers test doc doc-export print-success

test: dist-check test-output test-export

doc:
	$(call INVOKE_GUB,--offline $(BUILD_PLATFORM)) lilypond-doc

test-output:
	$(call INVOKE_GUB,--offline $(BUILD_PLATFORM)) lilypond-test

print-success:
	python test-lily/upload.py --branch=$(LILYPOND_BRANCH) --url $(LILYPOND_REPO_URL)
	@echo ""
	@echo "To upload, run "
	@echo
	@echo "        	python test-lily/upload.py --branch=$(LILYPOND_BRANCH) --url $(LILYPOND_REPO_URL) --execute "
	@echo

docball = uploads/lilypond-$(DIST_VERSION)-$(DOC_BUILDNUMBER).documentation.tar.bz2
webball = uploads/lilypond-$(DIST_VERSION)-$(DOC_BUILDNUMBER).webdoc.tar.bz2

$(docball):
#keep this target and just move/repackage lilypond-doc.gup,
#easier to handle versions.db?
	$(MAKE) doc

upload-setup-ini:
	cd uploads/cygwin && ../../downloads/genini $$(find release -mindepth 1 -maxdepth 2 -type d) > setup.ini

downloads/genini:
	wget --output-document $@ 'http://cygwin.com/cgi-bin/cvsweb.cgi/~checkout~/genini/genini?rev=1.2&content-type=text/plain&cvsroot=cygwin-apps&only_with_tag=HEAD'
	chmod +x $@

lily-clean:
	rm -rf target/$(BUILD_PLATFORM)/*/lilypond-$(LILYPOND_FLATTENED_BRANCH)*

lily-doc-clean:	doc-clean

clean:
	rm -rf $(foreach p, $(PLATFORMS), target/*$(p)* )

realclean:
	rm -rf $(foreach p, $(PLATFORMS), uploads/$(p)/* uploads/$(p)-cross/* target/*$(p)* )

################################################################
# compilers and tools

tools := $(shell $(GUB) --dependencies $(foreach p, $(PLATFORMS), $(p)::lilypond) 2>&1 | grep ^dependencies | tr ' ' '\n' | grep 'tools::')

################################################################
# docs

NATIVE_ROOT=$(NATIVE_TARGET_DIR)/installer/lilypond-$(LILYPOND_FLATTENED_BRANCH)
NATIVE_DOC_ROOT=$(NATIVE_TARGET_DIR)/installer/lilypond-$(LILYPOND_FLATTENED_BRANCH)-doc
DOC_LOCK=$(NATIVE_ROOT).lock
TEST_LOCK=$(NATIVE_ROOT).lock

NATIVE_LILY_BUILD=$(NATIVE_TARGET_DIR)/build/lilypond-$(LILYPOND_FLATTENED_BRANCH)
NATIVE_LILY_SRC=$(NATIVE_TARGET_DIR)/src/lilypond-$(LILYPOND_FLATTENED_BRANCH)
# URG: try to guess at what repository will do.  should ask
# repository.read_file(), I guess.
LILYPOND_REPO_DIR=downloads/lilypond/$(dir $(LILYPOND_DIRRED_BRANCH))
NATIVE_BUILD_COMMITTISH=$(shell cat $(LILYPOND_REPO_DIR)/refs/heads/$(LILYPOND_DIRRED_BRANCH))

print:
	@echo LDB $(LILYPOND_DIRRED_BRANCH)
	@echo LFB  $(LILYPOND_FLATTENED_BRANCH)

DIST_VERSION=$(shell cat $(NATIVE_LILY_BUILD)/out/VERSION)
DOC_BUILDNUMBER=$(shell $(PYTHON) gub/versiondb.py --platforms=$(PLATFORMS) --build-for=$(DIST_VERSION))

SIGNATURE_FUNCTION=uploads/signatures/$(1).$(NATIVE_BUILD_COMMITTISH)

doc-clean:
	$(PYTHON) gub/with-lock.py --skip $(DOC_LOCK) $(MAKE) unlocked-doc-clean

test-clean:
	$(PYTHON) gub/with-lock.py --skip $(TEST_LOCK) $(MAKE) unlocked-test-clean

unlocked-doc-clean:
	make -C $(NATIVE_TARGET_DIR)/build/lilypond-$(LILYPOND_FLATTENED_BRANCH) \
		DOCUMENTATION=yes web-clean
	rm -rf $(NATIVE_TARGET_DIR)/build/lilypond-$(LILYPOND_FLATTENED_BRANCH)/out/lybook-db
	rm -f $(call SIGNATURE_FUNCTION,cached-doc-build)
	rm -f $(call SIGNATURE_FUNCTION,cached-doc-export)

unlocked-test-clean:
	make -C $(NATIVE_TARGET_DIR)/build/lilypond-$(LILYPOND_FLATTENED_BRANCH) \
		DOCUMENTATION=yes test-clean
	rm -f $(call SIGNATURE_FUNCTION,cached-test-output)

cached-dist-check cached-doc-export:
	-mkdir uploads/signatures
	if test ! -f  $(call SIGNATURE_FUNCTION,$@) ; then \
		$(MAKE) $(subst cached,unlocked,$@) \
		&& touch $(call SIGNATURE_FUNCTION,$@) ; fi

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
		--branch=$(LILYPOND_BRANCH) \
		--url=$(LILYPOND_REPO_URL) \
		--repository=$(LILYPOND_REPO_DIR) $(NATIVE_LILY_BUILD)
	cp $(NATIVE_LILY_BUILD)/out/lilypond-$(DIST_VERSION).tar.gz uploads

dist-check:
	$(PYTHON) gub/with-lock.py --skip $(NATIVE_LILY_BUILD).lock \
		$(MAKE) cached-dist-check
