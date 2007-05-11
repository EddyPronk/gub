from gub import targetpackage
from gub import repository

url = 'http://tinylogin.busybox.net/downloads/tinylogin-1.4.tar.gz'

class Tinylogin (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_vc (repository.TarBall (self.settings.downloads, url))
    def patch (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
    def configure_command (self):
        return 'true'
    def makeflags (self):
        return 'CROSS=%(tool_prefix)s PREFIX=%(install_root)s'
    def install_command (self):
        return 'fakeroot make install %(makeflags)s'
    def license_file (self):
        return '%(srcdir)s/LICENSE'
