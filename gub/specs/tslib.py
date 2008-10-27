from gub import mirrors
from gub import targetbuild

class Tslib (targetbuild.AutoBuild):
    source = mirrors.with_tarball (name='tslib', mirror=mirrors.berlios, version='1.0', format='bz2')
    def configure (self):
        targetbuild.AutoBuild.configure (self)
        self.file_sub ([('#define malloc', '#define urg_malloc')],
                       '%(builddir)s/config.h')
    
