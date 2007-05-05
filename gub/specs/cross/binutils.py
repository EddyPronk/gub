from gub import cross
from gub import mirrors

class Binutils (cross.CrossToolSpec):
    def __init__ (self, settings):
        cross.CrossToolSpec.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.gnu, version='2.16.1', format='bz2')
    def install (self):
        cross.CrossToolSpec.install (self)
        self.system ('rm %(install_root)s/usr/cross/lib/libiberty.a')
