from gub import targetpackage
from gub import repository

url = 'http://busybox.net/downloads/busybox-1.5.1.tar.bz2'
# miscutils/taskset.c:18: warning: function declaration isn't a prototype
# cpu_set_t

class Busybox (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_vc (repository.TarBall (self.settings.downloads, url))
    def get_subpackage_names (self):
        return ['']
    def patch (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
        pass # FIXME: no ./configure, but do not run autoupdate
    def configure_command (self):
        return 'make -f %(srcdir)s/Makefile defconfig'
    def configure (self):
        targetpackage.TargetBuildSpec.configure (self)
        self.file_sub ([('^# CONFIG_FEATURE_SH_IS_ASH is not set', 'CONFIG_FEATURE_SH_IS_ASH=y'),
                        ('^CONFIG_FEATURE_SH_IS_NONE=y', '# CONFIG_FEATURE_SH_IS_NONE is not set'),
                        ], '%(builddir)s/.config')
    def makeflags (self):
        return ' CROSS_COMPILE=%(tool_prefix)s CONFIG_PREFIX=%(install_root)s'
    def license_file (self):
        return '%(srcdir)s/LICENSE'

# 1.5 is too new for glibc on vfp
class Busybox__linux__arm__vfp (Busybox):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        url = 'http://busybox.net/downloads/busybox-1.2.2.1.tar.bz2'
        self.with_vc (repository.TarBall (self.settings.downloads, url))
    def patch (self):
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/busybox-mkconfigs.patch
''')
        Busybox.patch (self)
    def makeflags (self):
        return ' CROSS=%(tool_prefix)s PREFIX=%(install_root)s'

                      
                                          
    

