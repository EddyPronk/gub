import mirrors
import misc
import repository
import targetpackage
#
import os

# Hmm? TARGET_CFLAGS=-O --> targetpackage.py

class Glibc (targetpackage.TargetBuildSpec):
    def patch (self):
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3-powerpc-initfini.patch
''')
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
                                      mirror=mirrors.glibc,
                                      name='glibc-linuxthreads',
                                      ball_version=self.version (),
                                      format='bz2',
                                      strip_components=0)
    def download (self):
        targetpackage.TargetBuildSpec.download (self)
        if self.version () == '2.3.6':
            self.linuxthreads ().download ()
    def untar (self):
        targetpackage.TargetBuildSpec.untar (self)
        if self.version () == '2.3.6':
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
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3-core-install.patch
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
