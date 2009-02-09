# local.make may set the following variables:
#
#  BUILD_PLATFORM  - override the platform used for building,
#                    if ./bin/build-platform should not work.
#
# it may set
#
#  GUB_CROSS_DISTCC_HOSTS - hosts with matching cross compilers
#  GUB_DISTCC_ALLOW_HOSTS - which distcc daemons may connect.
#  GUB_NATIVE_DISTCC_HOSTS - hosts with matching native compilers
#  LOCAL_GUB_OPTIONS - esp.: --verbose, --keep [--force-package]
#  LOCAL_GUB_BUILDER_OPTIONS - deprecated

.PHONY: bootstrap bootstrap-git
.PHONY: compilers cross-compilers
.PHONY: download
.PHONY: download-tools tools tools-cross-tools

ifeq ($(CWD),)
$(error Must set CWD)
endif
ifeq ($(PYTHON),)
$(error Must set PYTHON)
endif
ifeq ($(BUILD_PLATFORM),)
$(error Must set BUILD_PLATFORM)
endif

DISTCC_DIRS=target/cross-distcc/bin target/cross-distccd/bin target/native-distcc/bin 

# Find out if we need cross/gcc or glibc as topmost cross compile target
#gcc_or_glibc = $(shell $(GUB) -p $(1) --inspect=version glibc > /dev/null 2>/dev/null && echo glibc || echo cross/gcc)
gcc_or_glibc = $(shell if echo $(1) | grep linux > /dev/null 2>/dev/null; then echo glibc; else echo cross/gcc; fi)

tools = $(shell $(GUB) --dependencies $(foreach p, $(PLATFORMS), $(p)::$(call gcc_or_glibc,$(p))) 2>&1 | grep ^dependencies | tr ' ' '\n' | grep 'tools::')

compilers: cross-compilers

ifeq ($(BUILD_PLATFORM),)
$(error Must define BUILD_PLATFORM)
endif

cross-compilers:
	$(foreach p, $(PLATFORMS), $(call INVOKE_GUB,$(p)) $(call gcc_or_glibc,$(p)) && ) true

bootstrap: bootstrap-git download-tools tools cross-compilers tools-cross-tools download

bootstrap-git:
	$(GUB) $(LOCAL_GUB_OPTIONS) --platform=tools git

tools:
	$(GUB) $(LOCAL_GUB_OPTIONS) --platform=tools $(tools)

download-tools:
	$(GUB) $(LOCAL_GUB_OPTIONS) --platform=tools --stage=download $(tools) nsis

tools-cross-tools:
ifeq ($(findstring nsis, $(tools)),nsis)
	$(GUB) $(LOCAL_GUB_OPTIONS) --platform=tools nsis
endif

download:
