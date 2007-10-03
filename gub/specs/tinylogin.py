from gub import targetbuild
from gub import repository

url = 'http://tinylogin.busybox.net/downloads/tinylogin-1.4.tar.gz'

class Tinylogin (targetbuild.TargetBuild):
    source = mirrors.with_vc (repository.TarBall (self.settings.downloads, url))
    def patch (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
    def configure_command (self):
        return 'true'
    def makeflags (self):
        return 'CROSS=%(toolchain_prefix)s PREFIX=%(install_root)s'
    def install (self):
        fakeroot_cache = self.builddir () + '/fakeroot.cache'
        self.fakeroot (self.expand (self.settings.fakeroot, locals ()))
        targetbuild.TargetBuild.install (self)
    def install_command (self):
        return 'fakeroot make install %(makeflags)s'
