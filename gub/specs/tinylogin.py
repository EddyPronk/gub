from gub import targetpackage
from gub import repository

url = 'http://tinylogin.busybox.net/downloads/tinylogin-1.4.tar.gz'

class Tinylogin (targetpackage.TargetBuild):
    def __init__ (self, settings):
        targetpackage.TargetBuild.__init__ (self, settings)
        self.with_vc (repository.TarBall (self.settings.downloads, url))
    def patch (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
    def configure_command (self):
        return 'true'
    def makeflags (self):
        return 'CROSS=%(toolchain_prefix)s PREFIX=%(install_root)s'
    def install (self):
        fakeroot_cache = self.builddir () + '/fakeroot.cache'
        self.fakeroot (self.expand (self.settings.fakeroot, locals ()))
        targetpackage.TargetBuild.install (self)
    def install_command (self):
        return 'fakeroot make install %(makeflags)s'
    def license_file (self):
        return '%(srcdir)s/LICENSE'
