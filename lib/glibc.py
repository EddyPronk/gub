import download
import misc
import repository
import targetpackage
#
import os

# Hmm? TARGET_CFLAGS=-O --> targetpackage.py

class Glibc (targetpackage.TargetBuildSpec):
    #FIXME: what about apply_all (%(patchdir)s/%(version)s)?
    def patch_2_3_2 (self):
        self.system ('''
cd %(srcdir)s && patch -p0 < %(patchdir)s/glibc-linuxthreads-2.3.2-initfini.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3.2-output_format.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3.2-sysctl.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-vfp.patch
cd %(srcdir)s && patch -p0 < %(patchdir)s/glibc-2.3.2-arm-nobits.patch
cd %(srcdir)s && patch -p0 < %(patchdir)s/glibc-2.3.2-clobber-a1.patch
cd %(srcdir)s && patch -p0 < %(patchdir)s/glibc-2.3.2-sscanf.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3.2-arm-ctl_bus_isa.patch
''')
    def patch_2_3_6 (self):
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-linuxthreads-2.3.6-allow-3.4.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3.6-wordexp-inline.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3.2-arm-ctl_bus_isa.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-linuxthreads-2.3.6-allow-3.4-powerpc.patch
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3.6-allow-gcc-4.1-powerpc32-initfini.s.patch
''')
    def patch (self):
        if self.settings.package_arch == 'powerpc':
            self.file_sub ([('\$\(CFLAGS-pt-initfini.s\)',
                             '$(CFLAGS-pt-initfini.s) -fno-unit-at-a-time')],
                           '%(srcdir)s/linuxthreads/Makefile')
        self.system ('''
#rm -rf %(srcdir)s/nptl
''')
        self.class_invoke_version (Glibc, 'patch')
#--disable-sanity-checks
    def configure_command (self):
        add_ons = ''
        for i in ('linuxthreads',):
            # FIXME cannot expand in *_command ()
            #if os.path.exists (self.expand ('%(srcdir)s/') + i):
            if self.version () != '2.4':
                add_ons += ' --enable-add-ons=' + i
        return ('BUILD_CC=gcc '
                + misc.join_lines (targetpackage.TargetBuildSpec.configure_command (self) + '''
--disable-profile
--disable-debug
--without-cvs
--without-gd
--without-tls
--without-__thread
''')
                + add_ons)

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
        if self.version () != '2.4':
            self.linuxthreads ().download ()
    def untar (self):
        targetpackage.TargetBuildSpec.untar (self)
        if self.version () != '2.4':
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
    def patch_2_3_6 (self):
        Glibc.patch_2_3_6 (self)
    def patch (self):
        if self.settings.package_arch == 'powerpc':
            self.file_sub ([('\$\(CFLAGS-pt-initfini.s\)',
                             '$(CFLAGS-pt-initfini.s) -fno-unit-at-a-time')],
                           '%(srcdir)s/linuxthreads/Makefile')
        self.system ('''
#rm -rf %(srcdir)s/nptl
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3.6-make-install-lib-all.patch
''')
        self.class_invoke_version (Glibc_core, 'patch')
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
