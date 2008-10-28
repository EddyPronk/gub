from gub import context
from gub import targetbuild

# miscutils/taskset.c:18: warning: function declaration isn't a prototype
# cpu_set_t

class Busybox (targetbuild.AutoBuild):
    source = 'http://busybox.net/downloads/busybox-1.5.1.tar.bz2'
    def get_subpackage_names (self):
        return ['']
    def configure_command (self):
        return 'make -f %(srcdir)s/Makefile defconfig'
    @context.subst_method
    def autoconf_h (self):
        return 'autoconf.h'
    def configure (self):
        self.shadow ()
        targetbuild.AutoBuild.configure (self)
        self.file_sub ([('^# CONFIG_FEATURE_SH_IS_ASH is not set', 'CONFIG_FEATURE_SH_IS_ASH=y'),
                        ('^CONFIG_FEATURE_SH_IS_NONE=y', '# CONFIG_FEATURE_SH_IS_NONE is not set'),
                        ('^CONFIG_FEATURE_SH_STANDALONE_SHELL=y', '# CONFIG_FEATURE_SH_STANDALONE_SHELL is not set')],
                       '%(builddir)s/.config')
        self.system ('''rm -f %(builddir)s/include/%(autoconf_h)s
cd %(builddir)s && make include/%(autoconf_h)s > /dev/null 2>&1''')
    def makeflags (self):
        return ' CROSS_COMPILE=%(toolchain_prefix)s CONFIG_PREFIX=%(install_root)s'
    def install (self):
        targetbuild.AutoBuild.install (self)
        self.system ('''
cd %(install_root)s && mv sbin/init sbin/init.busybox
''')

# 1.5 is too new for glibc on vfp
class Busybox__linux__arm__vfp (Busybox):
    source = 'http://busybox.net/downloads/busybox-1.2.2.1.tar.bz2'
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
