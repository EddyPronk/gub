from gub import gubb
from gub import mirrors

class Gcc_gxx (gubb.NullBuildSpec):
    def __init__ (self, settings):
        gubb.NullBuildSpec.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.cygwin, version='3.4.4-3', format='bz2')
