from gub import targetpackage
from gub import repository

url = 'http://busybox.net/downloads/busybox-1.5.0.tar.bz2'

class Busybox (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_vc (repository.TarBall (self.settings.downloads, url))
    def patch (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
        pass # FIXME: no ./configure, but do not run autoupdate
    def configure_command (self):
        return 'make -f %(srcdir)s/Makefile defconfig'
    def makeflags (self):
        return ' CROSS_COMPILE=%(tool_prefix)s'
    def license_file (self):
        return '%(srcdir)s/LICENSE'
