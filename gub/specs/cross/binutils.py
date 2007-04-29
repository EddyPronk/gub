from gub import cross
from gub import mirrors

class Binutils (cross.Binutils):
    def __init__ (self, settings):
        cross.Binutils.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.gnu, version='2.16.1', format='bz2')

