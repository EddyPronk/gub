from gub import mirrors
from gub import repository
from gub import targetbuild

url = 'http://tinylogin.busybox.net/downloads/tinylogin-1.4.tar.gz'

class Tinylogin (targetbuild.MakeBuild):
    source = mirrors.with_vc (repository.TarBall (self.settings.downloads, url))
    def makeflags (self):
        return 'CROSS=%(toolchain_prefix)s PREFIX=%(install_root)s'
    def install (self):
        fakeroot_cache = self.builddir () + '/fakeroot.cache'
        self.fakeroot (self.expand (self.settings.fakeroot, locals ()))
        targetbuild.TargetBuild.install (self)
    def install_command (self):
        return 'fakeroot make install %(makeflags)s'
