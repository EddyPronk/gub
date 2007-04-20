import os
import re
#
import cross
import download
import gub
import targetpackage

class Freetype_config (gub.SdkBuildSpec):
    def __init__ (self, settings):
        gub.SdkBuildSpec.__init__ (self, settings)
        self.has_source = False

    def untar (self):
        pass

    def install (self):
        gub.SdkBuildSpec.install (self)
        self.system ('mkdir -p %(cross_prefix)s/usr/bin')
        
        ft_version = self.version ()
        prefix = '%(system_root)s/usr'
        exec_prefix = '${prefix}'
        includedir = '/usr/include'
        libdir = '/usr/lib'
        enable_shared = 'yes'
        wl = '-Wl,'
        hardcode_libdir_flag_spec='${wl}--rpath ${wl}$libdir'
        LIBZ = '-lz'

        s = open (self.expand ('%(sourcefiledir)s/freetype-config.in')).read ()
        s = re.sub (r'@(\w+?)@', r'%(\1)s', s)
        s = s % locals ()
        file = self.expand ('%(install_prefix)s/cross/bin/freetype-config')
        self.dump (s, file)
        os.chmod (file, 0755)

class Guile_config (gub.SdkBuildSpec):
    def __init__ (self, settings):
        gub.SdkBuildSpec.__init__ (self, settings)
        self.has_source = False

    def untar (self):
        pass

    def install (self):
        gub.SdkBuildSpec.install (self)
        self.system ('mkdir -p %(cross_prefix)s/usr/bin')
        
        version = self.version ()
	#FIXME: c&p guile.py
        self.dump ('''\
#! /bin/sh
test "$1" = "--version" && echo "%(target_architecture)s-guile-config - Guile version %(version)s"
#prefix=$(dirname $(dirname $0))
prefix=%(system_root)s/usr
test "$1" = "compile" && echo "-I$prefix/include"
#test "$1" = "link" && echo "-L$prefix/lib -lguile -lgmp"
# KUCH, debian specific, and [mipsel] reading .la is broken?
test "$1" = "link" && echo "-L$prefix/lib -lguile -lguile-ltdl  -ldl -lcrypt -lm"
exit 0
''',
             '%(install_prefix)s/cross/bin/%(target_architecture)s-guile-config')
        os.chmod ('%(install_prefix)s/cross/bin/%(target_architecture)s-guile-config'
                  % self.get_substitution_dict (), 0755)

class Python_config (gub.SdkBuildSpec):
    def __init__ (self, settings):
        gub.SdkBuildSpec.__init__ (self, settings)
        self.has_source = False

    def untar (self):
        pass

    # FIXME: c&p python.py:install ()
    def install (self):
        gub.SdkBuildSpec.install (self)
        self.system ('mkdir -p %(cross_prefix)s/usr/bin')
        cfg = open (self.expand ('%(sourcefiledir)s/python-config.py.in')).read ()
        cfg = re.sub ('@PYTHON_VERSION@', self.expand ('%(version)s'), cfg)
        cfg = re.sub ('@PREFIX@', self.expand ('%(system_root)s/usr/'), cfg)
        import sys
        cfg = re.sub ('@PYTHON_FOR_BUILD@', sys.executable, cfg)
        self.dump (cfg, '%(install_root)s/usr/cross/bin/python-config',
                   expand_string=False)
        self.system ('chmod +x %(install_root)s/usr/cross/bin/python-config')

def change_target_package (package):
    cross.change_target_package (package)
    if isinstance (package, targetpackage.TargetBuildSpec):
        gub.change_target_dict (package,
                        {'LD': '%(target_architecture)s-ld --as-needed ',
                        })

        gub.append_target_dict (package,
                                { 'LDFLAGS': ' -Wl,--as-needed ' })

    return package

def old_get_cross_packages (settings):
    import debian
    return debian.get_cross_packages (settings)

#FIXME, c&p linux-arm-softfloat.py
def _get_cross_packages (settings,
                         linux_version, binutils_version, gcc_version,
                         glibc_version, guile_version, python_version):
    configs = []
    if not settings.platform.startswith ('linux'):
        configs = [
            linux.Guile_config (settings).with (version=guile_version),
            linux.Python_config (settings).with (version=python_version),
            ]

    import linux_headers
    import debian
    import binutils
    import gcc
    import glibc
    headers = linux_headers.Linux_headers (settings)\
        .with_tarball (mirror=download.linux_2_4,
                       version=linux_version,
                       format='bz2')
    if settings.package_arch != 'i386':
        # other arch's need sane linux .config; where to get it?
        linux_version = '2.5.999-test7-bk-17'
        headers = debian.Linux_kernel_headers (settings)\
            .with (version=linux_version,
                   strip_components=0,
                   mirror=download.lilypondorg_deb,
                   format='deb')
    return [
        headers,
        binutils.Binutils (settings).with (version=binutils_version,
                                           format='bz2', mirror=download.gnu),
        gcc.Gcc_core (settings).with (version=gcc_version,
                                      mirror=download.gcc % {'name': 'gcc',
                                                             'ball_version': gcc_version,
                                                             'format': 'bz2',},
                                      format='bz2'),
        glibc.Glibc_core (settings).with (version=glibc_version,
                                          mirror=download.glibc % {'name': 'glibc',
                                                                   'ball_version': glibc_version,
                                                                   'format': 'bz2',},
                                          format='bz2'),
        gcc.Gcc (settings).with (version=gcc_version,
                                 mirror=download.gcc, format='bz2'),
        glibc.Glibc (settings).with (version=glibc_version, mirror=download.gnu,
                                     format='bz2'),
        ] + configs

def src_get_cross_packages (settings):
    linux_version = '2.4.34'
    #linux_version = '2.5.999-test7-bk-17'
    # 2.6 needs .config to make include/linux/version.h?
    #linux_version = '2.6.20.7'
    binutils_version = '2.16.1'
    gcc_version = '4.1.1'
    # gcc-core --disable-threads cannot booststrap glibc-2.4
    #glibc_version = '2.4' 
    glibc_version = '2.3.6'
    guile_version = '1.6.7'
    python_version = '2.4.1'
    return _get_cross_packages (settings,
                                linux_version, binutils_version,
                                gcc_version, glibc_version,
                                guile_version, python_version)

def get_cross_packages (settings):
    if settings.package_arch == 'powerpc':
        return old_get_cross_packages (settings)
    return src_get_cross_packages (settings)
        
    
    

