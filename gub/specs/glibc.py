from gub import mirrors
from gub import misc
from gub import repository
from gub import targetbuild
from gub import cross
#
import os

# Hmm? TARGET_CFLAGS=-O --> targetbuild.py

class Glibc (targetbuild.TargetBuild, cross.CrossToolsBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
        #self.with_tarball (mirror=mirrors.gnu, version='2.3.6')
    source = mirrors.with_tarball (name='glibc', mirror=mirrors.lilypondorg, version='2.3-20070416',
                           format='bz2')
    def get_build_dependencies (self):
        return ['cross/gcc', 'glibc-core']
    def get_conflict_dict (self):
        return {'': ['glibc-core'], 'devel': ['glibc-core'], 'doc': ['glibc-core'], 'runtime': ['glibc-core']}
    def patch (self):
        self.apply_patch ('glibc-2.3-powerpc-initfini.patch')
    def get_add_ons (self):
        return ('linuxthreads', 'nptl')
    def configure_command (self):    
        #FIXME: TODO, figure out which of --enable-add-ons=nptl,
        # --with-tls, --with-__thread fixes the ___tls_get_addr.
        add_ons = ''
        for i in self.get_add_ons ():
            # FIXME cannot expand in *_command ()
            #if os.path.exists (self.expand ('%(srcdir)s/') + i):
            if 1: #self.version () != '2.4':
                add_ons += ' --enable-add-ons=' + i
        return ('BUILD_CC=gcc '
                + misc.join_lines (targetbuild.TargetBuild.configure_command (self) + '''
--disable-profile
--disable-debug
--without-cvs
--without-gd
''')
#--without-tls
#--without-__thread
                + add_ons)
    def FIXME_DOES_NOT_WORK_get_substitution_dict (self, env={}):
        d = targetbuild.TargetBuild.get_substitution_dict (self, env)
        d['SHELL'] = '/bin/bash'
        return d
    def linuxthreads (self):
        return repository.get_repository_proxy (self.settings.downloads,
                                                self.expand ('ftp://ftp.gnu.org/pub/gnu/glibc/glibc-linuxthreads-%(version)s.tar.bz2&strip_components=0'))
    def download (self):
        targetbuild.TargetBuild.download (self)
        if self.version () == '2.3.6':
            self.linuxthreads ().download ()
    def untar (self):
        targetbuild.TargetBuild.untar (self)
        if self.version () == '2.3.6':
            self.linuxthreads ().update_workdir (self.expand ('%(srcdir)s/urg-do-not-mkdir-or-rm-me'))
            self.system ('mv %(srcdir)s/urg-do-not-mkdir-or-rm-me/* %(srcdir)s')
    def configure (self):
        targetbuild.TargetBuild.configure (self)
    def compile_command (self):
        return (targetbuild.TargetBuild.compile_command (self)
                + ' SHELL=/bin/bash')
    def install_command (self):
        return (targetbuild.TargetBuild.install_command (self)
                + ' install_root=%(install_root)s')
