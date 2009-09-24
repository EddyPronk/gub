from gub import cross
from gub.specs.cross import binutils as cross_binutils

class Binutils__darwin (cross_binutils.Binutils):
    # what's the story with odcctools?
    # it seems that darwin-ppc's binutils build as an empty shell?
    # instead, odcctools have the linker, assembler, etc?
    # Better to make odcctools an sdk package?
    # No, like this, that badly breaks dependencies.
    # Just *do not* build darwin-ppc::cross/binutils, that
    # triggers gcc to be built before odcctools?
    #def _get_build_dependencies (self):
    #    return (cross_binutils.Binutils.dependencies
    #            + ['odcctools'])
    def install (self):
        '''
        On some systems [Fedora9], libiberty.a is provided by binutils
        *and* by gcc; see gub/specs/binutils.py for more details.
        '''
        cross.AutoBuild.install (self)
        self.system ('rm %(install_prefix)s%(cross_dir)s/lib64/libiberty.a',
                     ignore_errors=True)
