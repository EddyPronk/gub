from gub import mirrors
from gub import misc
from gub import repository
from gub import targetbuild
from gub.specs import glibc

# Hmm? TARGET_CFLAGS=-O --> targetbuild.py

class Glibc_core (glibc.Glibc):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
        #self.with_tarball (mirror=mirrors.gnu, version='2.3.6')
    source = mirrors.with_tarball (mirror=mirrors.lilypondorg,
                           version='2.3-20070416', format='bz2', name='glibc')
    def get_build_dependencies (self):
        return ['cross/gcc-core']
    def get_subpackage_names (self):
        return ['']
    def get_conflict_dict (self):
        return {'': ['glibc', 'glibc-devel', 'glibc-doc', 'glibc-runtime']}
    def patch (self):
        glibc.Glibc.patch (self)
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/glibc-2.3-core-install.patch
''')
    def get_add_ons (self):
        return ('linuxthreads',)
    def configure_command (self):
        return (glibc.Glibc.configure_command (self)
                + misc.join_lines ('''
--without-tls
--without-__thread
'''))
    def compile_command (self):
        return (glibc.Glibc.compile_command (self)
                + ' lib')
    def install_command (self):
        return glibc.Glibc.install_command (self)
    def install_command (self):
        return (glibc.Glibc.install_command (self)
                    .replace (' install ', ' install-lib-all install-headers '))
    def install (self):
        glibc.Glibc.install (self)
        self.system ('''
mkdir -p %(install_prefix)s/include/gnu
touch %(install_prefix)s/include/gnu/stubs.h
cp %(srcdir)s/include/features.h %(install_prefix)s/include
mkdir -p %(install_prefix)s/include/bits
cp %(builddir)s/bits/stdio_lim.h %(install_prefix)s/include/bits
''')
