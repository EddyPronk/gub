.PHONY: all inkscape inkscape-installer

include gub.make

all: inkscape inkscape-installer print-success

PLATFORMS=$(BUILD_PLATFORM)
ALL_PLATFORMS=$(BUILD_PLATFORM)

inkscape:
	$(call INVOKE_GUB,$(BUILD_PLATFORM)) inkscape

inkscape-installer:
	$(call INVOKE_INSTALLER_BUILDER,$(BUILD_PLATFORM)) --branch=inkscape= inkscape

print-success:
	@echo installer: uploads/inkscape*$(BUILD_PLATFORM).sh
