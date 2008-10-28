from gub import targetbuild

class Tinylogin (targetbuild.MakeBuild):
    source = 'http://tinylogin.busybox.net/downloads/tinylogin-1.4.tar.gz'
    def makeflags (self):
        return 'CROSS=%(toolchain_prefix)s PREFIX=%(install_root)s'
    def install (self):
        fakeroot_cache = self.builddir () + '/fakeroot.cache'
        self.fakeroot (self.expand (self.settings.fakeroot, locals ()))
        targetbuild.AutoBuild.install (self)
    def install_command (self):
        return 'fakeroot make install %(makeflags)s'
