# -*-Makefile-*-
.PHONY: all default rest print-success

default: all

OPENOFFICE_BRANCH="" #master&revision=207309ec6d428c6a6698db061efb670b36d5df5a
OPENOFFICE_REPO_URL=git://anongit.freedesktop.org/git/ooo-build/ooo-build

PLATFORMS=mingw

# derived info
OPENOFFICE_SOURCE_URL=$(OPENOFFICE_REPO_URL)?branch=$(OPENOFFICE_BRANCH)
OPENOFFICE_DIRRED_BRANCH=$(shell $(PYTHON) gub/repository.py --branch-dir '$(OPENOFFICE_SOURCE_URL)')
OPENOFFICE_FLATTENED_BRANCH=$(shell $(PYTHON) gub/repository.py --full-branch-name '$(OPENOFFICE_SOURCE_URL)')
##BUILD_PACKAGE='$(OPENOFFICE_SOURCE_URL)'
BUILD_PACKAGE = openoffice
INSTALL_PACKAGE = openoffice

MAKE += -f openoffice.make

INSTALLER_BUILDER_OPTIONS =\
 --branch=ooo-build=$(OPENOFFICE_FLATTENED_BRANCH)

include gub.make
include compilers.make

all: packages rest
rest: openoffice-installers print-success

openoffice-installers:
	$(call INVOKE_INSTALLER_BUILDER,$(PLATFORMS)) $(INSTALL_PACKAGE)

print-success:
	@echo "success!!"
	@echo "OpenOffice installer in uploads/openoffice*exe"
