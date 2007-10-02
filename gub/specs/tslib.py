from gub import mirrors
from gub import targetbuild

class Tslib (targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
        self.with_tarball (mirror=mirrors.berlios, version='1.0', format='bz2')
    def configure (self):
        targetbuild.TargetBuild.configure (self)
        self.file_sub ([('#define malloc', '#define urg_malloc')],
                       '%(builddir)s/config.h')
    
