from gub import targetpackage
from gub import repository

url = 'http://matt.ucc.asn.au/dropbear/releases/dropbear-0.49.tar.gz'

class Dropbear (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_vc (repository.TarBall (self.settings.downloads, url))
    def get_build_dependencies (self):
        return ['zlib']
    def configure (self):
        targetpackage.TargetBuildSpec.configure (self)
        self.system ('''
mkdir -p %(builddir)s/libtomcrypt/src/mac/f9
mkdir -p %(builddir)s/libtomcrypt/src/mac/xcbc
mkdir -p %(builddir)s/libtomcrypt/src/math/fp
mkdir -p %(builddir)s/libtomcrypt/src/modes/f8
mkdir -p %(builddir)s/libtomcrypt/src/modes/lrw
''')
    def license_file (self):
        return '%(srcdir)s/LICENSE'
