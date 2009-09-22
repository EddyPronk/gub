import os
#
from gub import misc
from gub import tools

'''
Build shared libcoreutils.so without using libtool
for GUB's librestrict(2) to kick-in.
'''

no_patch = True # let's not use patch in a bootstrap package
class Coreutils__tools (tools.AutoBuild):
#    source = 'http://ftp.gnu.org/pub/gnu/coreutils/coreutils-6.12.tar.gz'
    source = 'http://ftp.gnu.org/pub/gnu/coreutils/coreutils-7.4.tar.gz'
    if 'BOOTSTRAP' in os.environ.keys ():
        patches = ['coreutils-6.12-shared-autoconf.patch']
    else:
        patches = ['coreutils-6.12-shared-automake.patch']
    if no_patch:
        patches = []
    def patch (self):
        if no_patch:
            self.file_sub ([('noinst_LIBRARIES', 'lib_LIBRARIES')],
                           '%(srcdir)s/lib/gnulib.mk')
            self.file_sub ([
                    (r'libcoreutils[.]a', 'libcoreutils.so'),
                    ('[.][.]/lib/libcoreutils.so ([$][(]LIBINTL[)]) [.][.]/lib/libcoreutils.so', r'-L../lib -lcoreutils \1'),
                    ], '%(srcdir)s/src/Makefile.in')
        else:
            tools.AutoBuild.patch (self)
    def _get_build_dependencies (self):
        if 'BOOTSTRAP' in os.environ.keys () or no_patch:
            return []
        return ['tools::autoconf', 'tools::automake']
    def force_autoupdate (self):
        return 'BOOTSTRAP' not in os.environ.keys () or no_patch
    def autoupdate (self):
        if 'BOOTSTRAP' in os.environ.keys () or no_patch:
            return
        self.system ('''
cd %(srcdir)s && autoreconf
''')
    def configure_command (self):
        return (tools.AutoBuild.configure_command (self)
                + ' CFLAGS=-fPIC')
    def makeflags (self):
        return misc.join_lines ('''
V=1
LDFLAGS='%(rpath)s'
LIBS='$(cp_LDADD) $(ls_LDADD) -lm'
RANLIB='mvaso () { test $$(basename $$1) == libcoreutils.a && mv $$1 $$(dirname $$1)/$$(basename $$1 .a).so || : ; }; mvaso '
libcoreutils_a_AR='gcc -shared -o'
''')
    def install (self):
        # The RANLIB/mvaso trick needs libcoreutils.a to exist at install time.
        self.system ('cd %(builddir)s/lib && ln -f libcoreutils.so libcoreutils.a')
        tools.AutoBuild.install (self)
        self.system ('cd %(builddir)s/lib && rm -f libcoreutils.a')
        if 'BOOTSTRAP' in os.environ.keys () or no_patch:
            self.system ('mkdir -p %(install_prefix)s/lib')
            self.system ('cp -pv %(builddir)s/lib/libcoreutils* %(install_prefix)s/lib')
