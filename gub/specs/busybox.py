from gub import mirrors
from gub import targetbuild
from gub import repository
from gub import context

url = 'http://busybox.net/downloads/busybox-1.5.1.tar.bz2'
# miscutils/taskset.c:18: warning: function declaration isn't a prototype
# cpu_set_t

class Busybox (targetbuild.TargetBuild):
    source = mirrors.with_vc (repository.TarBall (self.settings.downloads, url))
    def get_subpackage_names (self):
        return ['']
    def patch (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
        pass # FIXME: no ./configure, but do not run autoupdate
    def configure_command (self):
        return 'make -f %(srcdir)s/Makefile defconfig'
    @context.subst_method
    def autoconf_h (self):
        return 'autoconf.h'
    def configure (self):
        targetbuild.TargetBuild.configure (self)
        self.file_sub ([('^# CONFIG_FEATURE_SH_IS_ASH is not set', 'CONFIG_FEATURE_SH_IS_ASH=y'),
                        ('^CONFIG_FEATURE_SH_IS_NONE=y', '# CONFIG_FEATURE_SH_IS_NONE is not set'),
                        ('^CONFIG_FEATURE_SH_STANDALONE_SHELL=y', '# CONFIG_FEATURE_SH_STANDALONE_SHELL is not set')],
                       '%(builddir)s/.config')
        self.system ('''rm -f %(builddir)s/include/%(autoconf_h)s
cd %(builddir)s && make include/%(autoconf_h)s > /dev/null 2>&1''')
    def makeflags (self):
        return ' CROSS_COMPILE=%(toolchain_prefix)s CONFIG_PREFIX=%(install_root)s'
    def install (self):
        targetbuild.TargetBuild.install (self)
        self.system ('''
cd %(install_root)s && mv sbin/init sbin/init.busybox
''')

# 1.5 is too new for glibc on vfp
class Busybox__linux__arm__vfp (Busybox):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
        url = 'http://busybox.net/downloads/busybox-1.2.2.1.tar.bz2'
    source = mirrors.with_vc (repository.TarBall (self.settings.downloads, url))
    def patch (self):
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/busybox-mkconfigs.patch
''')
        Busybox.patch (self)
    def makeflags (self):
        return ' CROSS=%(toolchain_prefix)s PREFIX=%(install_root)s'
    @context.subst_method
    def autoconf_h (self):
        return 'bb_config.h'
