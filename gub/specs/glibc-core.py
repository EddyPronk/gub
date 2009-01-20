from gub import misc
from gub import target
from gub.specs import glibc

# Hmm? TARGET_CFLAGS=-O --> target.py

class Glibc_core (glibc.Glibc):
    source = 'http://lilypond.org/download/gub-sources/glibc-2.3-20070416.tar.bz2'
    patches = glibc.Glibc.patches + ['glibc-2.3-core-install.patch']
    def get_build_dependencies (self):
        return ['cross/gcc-core', 'linux-headers']
    def get_subpackage_names (self):
        return ['']
    def get_conflict_dict (self):
        return {'': ['glibc', 'glibc-devel', 'glibc-doc', 'glibc-runtime']}
    def get_add_ons (self):
        return ('linuxthreads',)
    def configure_command (self):
        return (glibc.Glibc.configure_command (self)
#                .replace ('--disable-versioning', '--enable-versioning')
                + misc.join_lines ('''
--without-tls
--without-__thread
'''))

    # Disable librestrict.so, as it causes crashes on Fedora 9 and 10.
    def LD_PRELOAD (self):
        return ''
    
    def compile_command (self):
        return (glibc.Glibc.compile_command (self)
                + ' lib')
    def compile (self):
        target.AutoBuild.compile (self)

    # TODO: docme: why does the compile not have gnulib=-lgcc ?
    def install_command (self):
        return (glibc.Glibc.install_command (self)
                .replace (' install ', ' install-lib-all install-headers ')
                # avoid -lgcc_eh, which gcc-core does not have
                + ' gnulib=-lgcc')
    def install (self):
        glibc.Glibc.install (self)
        self.system ('''
mkdir -p %(install_prefix)s/include/gnu
touch %(install_prefix)s/include/gnu/stubs.h
cp %(srcdir)s/include/features.h %(install_prefix)s/include
mkdir -p %(install_prefix)s/include/bits
cp %(builddir)s/bits/stdio_lim.h %(install_prefix)s/include/bits
''')

class Glibc_core__linux__ppc (Glibc_core):
    patches = Glibc_core.patches
    def install_command (self):
        # ugh, but the gnulib=-lgcc hack does something else on ppc...
        # it (huh?) drops *-lgcc* (instead of -lgcc_eh) from libc.so
        # linkage, which then fails.
        return Glibc_core.install_command (self).replace (' gnulib=-lgcc', '')
