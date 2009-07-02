# -*-Makefile-*-
.PHONY: all default rest print-success
.PHONY: nsis denemo denemo-installers
default: all

DENEMO_BRANCH="master"
DENEMO_REPO_URL=git://git.savannah.gnu.org/denemo.git

PLATFORMS=mingw

# derived info
DENEMO_SOURCE_URL=$(DENEMO_REPO_URL)?branch=$(DENEMO_BRANCH)
DENEMO_DIRRED_BRANCH=$(shell $(PYTHON) gub/repository.py --branch-dir '$(DENEMO_SOURCE_URL)')
DENEMO_FLATTENED_BRANCH=$(shell $(PYTHON) gub/repository.py --full-branch-name '$(DENEMO_SOURCE_URL)')
# FOR BUILDING from GIT
#BUILD_PACKAGE='$(DENEMO_SOURCE_URL)'
BUILD_PACKAGE=denemo
INSTALL_PACKAGE = denemo

MAKE += -f denemo.make

# FOR BUILDING from GIT
#INSTALLER_BUILDER_OPTIONS =\
# --branch=denemo=$(DENEMO_FLATTENED_BRANCH)

include gub.make
include compilers.make

#all: packages rest
all: denemo rest
rest: nsis denemo-installers print-success

#avoid building native BUILD_PLATFORM
denemo:
	$(call INVOKE_GUB,$(PLATFORMS)) denemo

denemo-installers:
	$(call INVOKE_INSTALLER_BUILDER,$(PLATFORMS)) $(INSTALL_PACKAGE)

nsis:
	bin/gub tools::nsis

print-success:
	@echo "success!!"
	@echo Denemo installer in uploads/denemo*.mingw.exe
