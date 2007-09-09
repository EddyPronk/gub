from gub import cross
from gub import mirrors

class Odcctools (cross.CrossToolSpec):
    def __init__ (self, settings):
        cross.CrossToolSpec.__init__ (self, settings)
        self.with_template (version='20060413',
                   ####version='20060608',
                   #version='20061117',
                   mirror=mirrors.opendarwin,
                   format='bz2')
        # odcctools does not build with 64 bit compiler
        if settings.build_architecture.startswith ('x86_64-linux'):
            cross.setup_linux_x86 (self)
    def get_build_dependencies (self):
        return ['darwin-sdk']
    def configure (self):
        cross.CrossToolSpec.configure (self)
        ## remove LD64 support.
        self.file_sub ([('ld64','')], self.builddir () + '/Makefile')
