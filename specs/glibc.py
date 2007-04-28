import mirrors
import misc
import repository
import targetpackage
#
import os

# Hmm? TARGET_CFLAGS=-O --> targetpackage.py

class Glibc (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        #self.with_tarball (mirror=mirrors.gnu, version='2.3.6')
        self.with_tarball (mirror=mirrors.lilypondorg, version='2.3-20070416',
                           format='bz2')
    def get_build_dependencies (self):
        return ['gcc', 'glibc-core']
    def get_conflict_dict (self):
        return {'': ['glibc-core'], 'devel': ['glibc-core'], 'doc': ['glibc-core'], 'runtime': ['glibc-core']}
    def patch (self):
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3-powerpc-initfini.patch
''')
    def configure_command (self):
        add_ons = ''
        for i in ('linuxthreads',):
            # FIXME cannot expand in *_command ()
            #if os.path.exists (self.expand ('%(srcdir)s/') + i):
            if 1: #self.version () != '2.4':
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
