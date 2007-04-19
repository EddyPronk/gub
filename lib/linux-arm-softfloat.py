import os
import re
#
import cross
import download
import gub
import linux
import misc
import targetpackage
import repository


# Hmm? TARGET_CFLAGS=-O

class Linux_arm_softfloat_runtime (gub.BinarySpec, gub.SdkBuildSpec):
    pass

class Gcc (cross.Gcc):
    def patch_3_4_0 (self):
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/gcc-3.4.0-arm-softfloat.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/gcc-3.4.0-arm-lib1asm.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/gcc-3.4.0-arm-nolibfloat.patch
''')
    def patch (self):
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/gcc-3.4.0-arm-lib1asm.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/gcc-3.4.0-arm-nolibfloat.patch
''')
    def get_build_dependencies (self):
        return cross.Gcc.get_build_dependencies (self) + ['gcc-core', 'glibc-core']
    def get_conflict_dict (self):
        return {'': ['gcc-core'], 'doc': ['gcc-core'], 'runtime': ['gcc-core']}
    def configure_command (self):
        return (cross.Gcc.configure_command (self)
                + misc.join_lines ('''
--with-local-prefix=%(system_root)s/usr
--disable-multilib
--disable-nls
--enable-threads=posix
--enable-__cxa_atexit
--enable-symvers=gnu
--with-float=soft
'''))
    def install (self):
        cross.Gcc.install (self)
        self.system ('''
mv %(install_root)s/usr/cross/lib/gcc/%(target_architecture)s/%(version)s/libgcc_eh.a %(install_root)s/usr/lib
''')
        

class Gcc_core (Gcc):
    def __init__ (self, settings):
        Gcc.__init__ (self, settings)
    def get_subpackage_names (self):
        return ['']
    def name (self):
        return 'gcc-core'
    def file_name (self):
        return 'gcc-core'
    def get_build_dependencies (self):
        return cross.Gcc.get_build_dependencies (self) + ['binutils']
    def get_conflict_dict (self):
        return {'': ['gcc', 'gcc-devel', 'gcc-doc', 'gcc-runtime']}
    def configure_command (self):
        return (misc.join_lines (Gcc.configure_command (self) + '''
--prefix=%(cross_prefix)s
--prefix=/usr
--with-newlib
--enable-threads=no
--without-headers
--disable-shared
''')
                .replace ('enable-shared', 'disable-shared')
                .replace ('disable-static', 'enable-static')
                .replace ('enable-threads=posix', 'enable-threads=no'))
    def compile_command (self):
        return (cross.Gcc.compile_command (self) + ' all-gcc')
    def compile (self):
        cross.Gcc.compile (self)
    def install_command (self):
        return (Gcc.install_command (self)
                .replace (' install', ' install-gcc')
                #+ ' prefix=/usr/cross/core'
                )
    def install (self):
        # cross.Gcc moves libs into system lib places, which will
        # make gcc-core conflict with gcc.
        cross.CrossToolSpec.install (self)
    def languages (self):
        return  ['c']

class Glibc (targetpackage.TargetBuildSpec):
    #FIXME: what about apply_all (%(patchdir)s/%(version)s)?
    def patch_2_3_2 (self):
        self.system ('''
#cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-linuxthreads-2.3.2-allow-3.4.patch
cd %(srcdir)s && patch -p0 < %(patchdir)s/glibc-linuxthreads-2.3.2-initfini.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3.2-output_format.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3.2-sysctl.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-vfp.patch
cd %(srcdir)s && patch -p0 < %(patchdir)s/glibc-2.3.2-arm-nobits.patch
cd %(srcdir)s && patch -p0 < %(patchdir)s/glibc-2.3.2-clobber-a1.patch
cd %(srcdir)s && patch -p0 < %(patchdir)s/glibc-2.3.2-sscanf.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3.2-arm-ctl_bus_isa.patch
''')

    def patch (self):
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3.6-wordexp-inline.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3.2-arm-ctl_bus_isa.patch
##cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3.6-make-install-lib-all.patch
''')

#--disable-sanity-checks
    def configure_command (self):
        return 'BUILD_CC=gcc ' + misc.join_lines (targetpackage.TargetBuildSpec.configure_command (self) + '''
--enable-add-ons=linuxthreads
--disable-profile
--disable-debug
--without-cvs
--without-gd
--without-fp
--without-tls
--without-__thread
''')
    def get_build_dependencies (self):
        return ['gcc-core']
    def get_conflict_dict (self):
        return {'': ['glibc-core'], 'devel': ['glibc-core'], 'doc': ['glibc-core'], 'runtime': ['glibc-core']}
    def FIXME_DOES_NOT_WORK_get_substitution_dict (self, env={}):
        d = targetpackage.TargetBuildSpec.get_substitution_dict (self, env)
        d['SHELL'] = '/bin/bash'
        return d
    def linuxthreads (self):
        return repository.NewTarBall (dir=self.settings.downloads,
                                      mirror=download.glibc,
                                      name='glibc-linuxthreads',
                                      ball_version=self.version (),
                                      format='bz2',
                                      strip_components=0)
    def do_download (self):
        targetpackage.TargetBuildSpec.do_download (self)
        self.linuxthreads ().download ()
    def untar (self):
        targetpackage.TargetBuildSpec.untar (self)
        self.linuxthreads ().update_workdir (self.expand ('%(srcdir)s/urg-do-not-mkdir-or-rm-me'))
        self.system ('mv %(srcdir)s/urg-do-not-mkdir-or-rm-me/* %(srcdir)s')
    def configure (self):
        targetpackage.TargetBuildSpec.configure (self)
    def compile_command (self):
        return (targetpackage.TargetBuildSpec.compile_command (self)
                + ' SHELL=/bin/bash')
    def install_command (self):
        return (targetpackage.TargetBuildSpec.install_command (self)
                + ' install_root=%(install_root)s')

class Glibc_core (Glibc):
    def get_subpackage_names (self):
        return ['']
    def get_conflict_dict (self):
        return {'': ['glibc', 'glibc-devel', 'glibc-doc', 'glibc-runtime']}
    def patch (self):
        Glibc.patch (self)
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3.6-make-install-lib-all.patch
''')
    def compile_command (self):
        return (Glibc.compile_command (self)
                + ' lib')
    def install_command (self):
        return Glibc.install_command (self)
    def install_command (self):
        return (Glibc.install_command (self)
                    .replace (' install ', ' install-lib-all install-headers '))
    def install (self):
        Glibc.install (self)
        self.system ('''
mkdir -p %(install_root)s/usr/include/gnu
touch %(install_root)s/usr/include/gnu/stubs.h
cp %(srcdir)s/include/features.h %(install_root)s/usr/include
mkdir -p %(install_root)s/usr/include/bits
cp %(builddir)s/bits/stdio_lim.h %(install_root)s/usr/include/bits
''')

def _get_cross_packages (settings,
                         binutils_version, gcc_version,
                         guile_version, kernel_version, glibc_version,
                         python_version):
    configs = []
    if not settings.platform.startswith ('linux'):
        configs = [
            linux.Guile_config (settings).with (version=guile_version),
            linux.Python_config (settings).with (version=python_version),
            ]

    import debian
    return [
        debian.Linux_kernel_headers (settings).with (version=kernel_version,
                                                     strip_components=0,
                                                     mirror=download.lilypondorg_deb,
                                                     format='deb'),
        
        cross.Binutils (settings).with (version=binutils_version,
                                        format='bz2', mirror=download.gnu),
        Gcc_core (settings).with (version=gcc_version,
                                  mirror=download.gcc % {'name': 'gcc',
                                                         'ball_version': gcc_version,
                                                         'format': 'bz2',},
                                  format='bz2'),
        Glibc_core (settings).with (version=glibc_version,
                                    mirror=download.glibc % {'name': 'glibc',
                                                             'ball_version': glibc_version,
                                                             'format': 'bz2',},
                                    format='bz2'),
        Gcc (settings).with (version=gcc_version,
                             mirror=download.gcc, format='bz2'),
        Glibc (settings).with (version=glibc_version, mirror=download.gnu,
                               format='bz2'),
        ] + configs

def get_cross_packages (settings):
    #import debian
    #return debian.get_cross_packages (settings)
    return get_cross_packages_pre_eabi (settings)

def get_cross_packages_pre_eabi (settings):
    binutils_version = '2.16.1'
    #gcc_version = '3.4.0'
    gcc_version = '3.4.5'
    guile_version = '1.6.7'
    kernel_version = '2.5.999-test7-bk-17'
    #glibc_version = '2.3.2.ds1-22sarge4'
    #glibc_version = '2.3.2'
    glibc_version = '2.3.6'
    python_version = '2.4.1'
    #import debian
    return _get_cross_packages (settings,
                                binutils_version, gcc_version,
                                guile_version,
                                kernel_version, glibc_version,
                                python_version)

def change_target_package (p):
    cross.change_target_package (p)
    return p
