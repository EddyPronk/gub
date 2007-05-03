
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
#  LOCAL_GUB_BUILDER_OPTIONS - esp.: --verbose, --keep [--force-package]

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

default: cross-compilers
compilers: cross-compilers

-include local.make

ifeq ($(BUILD_PLATFORM),)
$(error Must define BUILD_PLATFORM)
endif

distccd: clean-distccd cross-compilers cross-distccd native-distccd local-distcc

clean-distccd:
	rm -rf $(DISTCC_DIRS)
	mkdir -p $(DISTCC_DIRS)

local-distcc:
	chmod +x gub/distcc.py
	rm -rf target/native-distcc/bin/ target/cross-distcc/bin/
	mkdir -p target/cross-distcc/bin/ target/native-distcc/bin/
	$(foreach binary,$(foreach p,$(PLATFORMS), $(filter-out %/python-config,$(wildcard target/$(p)/system/usr/cross/bin/*))), \
		ln -s $(CWD)/gub/distcc.py target/cross-distcc/bin/$(notdir $(binary)) && ) true
	$(foreach binary, gcc g++, \
		ln -s $(CWD)/gub/distcc.py target/native-distcc/bin/$(notdir $(binary)) && ) true

# Find out if we need cross/gcc or glibc as topmost cross compile target
#gcc_or_glibc = $(shell $(GUB_BUILDER) -p $(1) --inspect=version glibc > /dev/null 2>/dev/null && echo glibc || echo cross/gcc)

# URG
gcc_or_glibc = $(shell if echo $(1) | grep linux > /dev/null 2>/dev/null; then echo glibc; else echo cross/gcc; fi)

cross-compilers:
	$(foreach p, $(PLATFORMS),$(call INVOKE_GUB_BUILDER, $(p)) $(call gcc_or_glibc, $(p)) && ) true

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
	$(GUB_BUILDER) $(LOCAL_GUB_BUILDER_OPTIONS) -p local git

local-cross-tools:
ifneq ($(filter mingw,$(PLATFORMS)),)
ifneq ($(BUILD_PLATFORM),linux-64)
	$(GUB_BUILDER) $(LOCAL_DRIVER_OPTIONS) -p local nsis 
endif
endif

