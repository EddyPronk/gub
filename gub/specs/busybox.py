from gub import context
from gub import tools
from gub import target

# miscutils/taskset.c:18: warning: function declaration isn't a prototype
# cpu_set_t

class Busybox (target.AutoBuild):
    source = 'http://busybox.net/downloads/busybox-1.5.1.tar.bz2'
    srcdir_build_broken = True
    subpackage_names = ['']
    def configure_command (self):
        return 'make -f %(srcdir)s/Makefile defconfig'
    @context.subst_method
    def autoconf_h (self):
        return 'autoconf.h'
    def configure (self):
        target.AutoBuild.configure (self)
        self.file_sub ([('^# CONFIG_FEATURE_SH_IS_ASH is not set', 'CONFIG_FEATURE_SH_IS_ASH=y'),
                        ('^CONFIG_FEATURE_SH_IS_NONE=y', '# CONFIG_FEATURE_SH_IS_NONE is not set'),
                        ('^CONFIG_FEATURE_SH_STANDALONE_SHELL=y', '# CONFIG_FEATURE_SH_STANDALONE_SHELL is not set')],
                       '%(builddir)s/.config')
        self.system ('''rm -f %(builddir)s/include/%(autoconf_h)s
cd %(builddir)s && make include/%(autoconf_h)s > /dev/null 2>&1''')
    make_flags = ' CROSS_COMPILE=%(toolchain_prefix)s CONFIG_PREFIX=%(install_root)s'
    def install (self):
        target.AutoBuild.install (self)
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
    make_flags = ' CROSS=%(toolchain_prefix)s PREFIX=%(install_root)s'
    @context.subst_method
    def autoconf_h (self):
        return 'bb_config.h'

class Busybox__tools (tools.AutoBuild, Busybox):
    source = 'http://busybox.net/downloads/busybox-1.13.2.tar.gz'
    srcdir_build_broken = True
    configure_command = 'make -f %(srcdir)s/Makefile defconfig'
    @context.subst_method
    def autoconf_h (self):
        return 'autoconf.h'
    def configure (self):
#        tools.AutoBuild.configure (self)
        self.system ('cd %(builddir)s && %(configure_command)s')
        self.file_sub ([
                ('^# CONFIG_FEATURE_SH_IS_ASH is not set', 'CONFIG_FEATURE_SH_IS_ASH=y'),
                ('^CONFIG_FEATURE_SH_IS_NONE=y', '# CONFIG_FEATURE_SH_IS_NONE is not set'),
                ('^CONFIG_FEATURE_SH_STANDALONE_SHELL=y', '# CONFIG_FEATURE_SH_STANDALONE_SHELL is not set'),
                ('^CONFIG_AR=y', '# CONFIG_AR is not set'),
                ('^CONFIG_BUNZIP2=y', '# CONFIG_BUNZIP2 is not set'),
                ('^CONFIG_BZ2=y', '# CONFIG_BZ2 is not set'),
                ('^CONFIG_FEATURE_SEAMLESS_BZ2=y', '# CONFIG_FEATURE_SEAMLESS_BZ2 is not set'),
                ('^CONFIG_BZIP2=y', '# CONFIG_BZIP2 is not set'),
                ('^CONFIG_CLEAR=y', '# CONFIG_CLEAR is not set'),
                ('^CONFIG_PATCH=y', '# CONFIG_PATCH is not set'),
                ('^CONFIG_RESET=y', '# CONFIG_RESET is not set'),
                ('^CONFIG_TAR=y', '# CONFIG_TAR is not set'),
                ],
                       '%(builddir)s/.config')
        self.system ('''rm -f %(builddir)s/include/%(autoconf_h)s
cd %(builddir)s && make include/%(autoconf_h)s > /dev/null 2>&1''')
    make_flags = ' CONFIG_PREFIX=%(install_prefix)s'
    def install (self):
        tools.AutoBuild.install (self)
        self.system ('''
cd %(install_prefix)s && mv sbin/init sbin/init.busybox
''')
