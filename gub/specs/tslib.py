from gub import mirrors
from gub import targetpackage

class Tslib (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.berlios, version='1.0', format='bz2')
    def configure (self):
        targetpackage.TargetBuildSpec.configure (self)
        self.file_sub ([('#define malloc', '#define urg_malloc')],
                       '%(builddir)s/config.h')
    
