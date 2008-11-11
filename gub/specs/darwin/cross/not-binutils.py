from gub.specs.cross import binutils

class Binutils__darwin (binutils.Binutils):
    patches = binutils.Binutils.patches
    # what's the story with odcctools?
    # it seems that darwin-ppc's binutils build as an empty shell?
    # instead, odcctools have the linker, assembler, etc?
    # Better to make odcctools an sdk package?
    # No, like this, that badly breaks dependencies.
    # Just *do not* build darwin-ppc::cross/binutils, that
    # triggers gcc to be built before odcctools?
    def get_build_dependencies (self):
        return (binutils.Binutils.get_build_dependencies (self)
                + ['odcctools'])
