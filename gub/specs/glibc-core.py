from gub import misc
from gub import target
from gub.specs import glibc

# Hmm? TARGET_CFLAGS=-O --> target.py

class Glibc_core (glibc.Glibc):
    source = 'http://lilypond.org/download/gub-sources/glibc-2.3-20070416.tar.bz2'
    patches = glibc.Glibc.patches + ['glibc-2.3-core-install.patch']
    dependencies = ['cross/gcc-core', 'linux-headers', 'tools::bison']
    configure_flags = (glibc.Glibc.configure_flags
                       + misc.join_lines ('''
--without-tls
--without-__thread
'''))
    make_flags = (glibc.Glibc.make_flags
                  # avoid -lgcc_eh, which gcc-core does not have
                  + ' gnulib=-lgcc')
    compile_flags = glibc.Glibc.compile_flags + ' lib'
    install_flags = (glibc.Glibc.install_flags
                     .replace (' install ', ' install-lib-all install-headers '))
    subpackage_names = ['']
    def get_conflict_dict (self):
        return {'': ['glibc', 'glibc-devel', 'glibc-doc', 'glibc-runtime']}
    def get_add_ons (self):
        return ('linuxthreads',)
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
        # ugh, but the gnulib=-lgcc hack does something else on ppc...
        # it (huh?) drops *-lgcc* (instead of -lgcc_eh) from libc.so
        # linkage, which then fails.
    make_flags = glibc.Glibc.make_flags

class Glibc_core__linux__mipsel (Glibc_core):
    patches = Glibc_core.patches + [
        'glibc-2.3-mips-syscall.patch',
        ]
