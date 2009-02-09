.PHONY: all gub3-packages gub3-installers
.PHONY: inkscape inkscape-installer inkscape-installers print-success

include gub.make

all: inkscape inkscape-installer print-success

INKSCAPE_BRANCH=trunk?revision=20605
INKSCAPE_REPO_URL=svn:https://inkscape.svn.sourceforge.net/svnroot/inkscape?module=inkscape
#source = 'svn:https://inkscape.svn.sourceforge.net/svnroot/inkscape&module=inkscape&branch=trunk&revision=20605'

PLATFORMS=linux-x86
# cocoa?
# PLATFORMS+=darwin-ppc darwin-x86
# nsis does not build with 64 bit compiler
PLATFORMS+=mingw
PLATFORMS+=linux-64
PLATFORMS+=linux-ppc
PLATFORMS+=freebsd-x86 freebsd-64
#PLATFORMS+=cygwin

PLATFORMS=$(BUILD_PLATFORM)

#derived info
INKSCAPE_SOURCE_URL=$(INKSCAPE_REPO_URL)?branch=$(INKSCAPE_BRANCH)
INKSCAPE_DIRRED_BRANCH=$(shell $(PYTHON) gub/repository.py --branch-dir '$(INKSCAPE_SOURCE_URL)')
INKSCAPE_FLATTENED_BRANCH=$(shell $(PYTHON) gub/repository.py --full-branch-name '$(INKSCAPE_SOURCE_URL)')

BUILD_PACKAGE='$(INKSCAPE_SOURCE_URL)'
INSTALL_PACKAGE = inkscape

MAKE += -f lilypond.make

gub3-packages:
	$(call INVOKE_GUB,$(BUILD_PLATFORM)) $(BUILD_PACKAGE) $(OTHER_PLATFORMS:%=%::$(BUILD_PACKAGE))

gub3-installers: #gub3-packages
	$(foreach p,$(PLATFORMS),$(call INVOKE_INSTALLER_BUILDER,$(p)) $(INSTALL_PACKAGE) && ) :

inkscape: gub3-packages

inkscape-installer: gub3-installers
inkscape-installers: gub3-installers

print-success:
	@echo installer: uploads/inkscape*$(BUILD_PLATFORM).sh
