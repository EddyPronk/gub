from gub import cross
from gub import mirrors

class Odcctools (cross.CrossToolSpec):
    def __init__ (self, settings):
        cross.CrossToolSpec.__init__ (self, settings)
        self.with (version='20060413',
                   # version='20060608',
                   mirror=mirrors.opendarwin,
                   format='bz2')
    def get_build_dependencies (self):
        return ['darwin-sdk']
    def configure (self):
        cross.CrossToolSpec.configure (self)
        ## remove LD64 support.
        self.file_sub ([('ld64','')], self.builddir () + '/Makefile')
