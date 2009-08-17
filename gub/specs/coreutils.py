import os
#
from gub import tools

'''
Build shared libcoreutils.so without using libtool
for GUB's librestrict(2) to kick-in.
'''

class Coreutils__tools (tools.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/coreutils/coreutils-6.12.tar.gz'
    if 'BOOTSTRAP' in os.environ.keys ():
        patches = ['coreutils-6.12-shared-autoconf.patch']
    else:
        patches = ['coreutils-6.12-shared-automake.patch']
    def _get_build_dependencies (self):
        return ['tools::autoconf', 'tools::automake']
    def force_autoupdate (self):
        return 'BOOTSTRAP' not in os.environ.keys ()
    def autoupdate (self):
        if not 'BOOTSTRAP' in os.environ.keys ():
            self.system ('''
cd %(srcdir)s && autoreconf
''')
    def configure_command (self):
        return (tools.AutoBuild.configure_command (self)
                + ' CFLAGS=-fPIC')
    def makeflags (self):
        return ''' LDFLAGS='%(rpath)s' LIBS='$(cp_LDADD) $(ls_LDADD) -lm' RANLIB='mvaso () { mv $$1 $$(dirname $$1)/$$(basename $$1 .a).so; }; mvaso ' libcoreutils_a_AR='gcc -shared -o' '''
    def wrap_executables (self):
        # using rpath
        pass
    def install (self):
        # The RANLIB/mvaso trick needs libcoreutils.a to exist at install time.
        self.system ('cd %(builddir)s/lib && ln libcoreutils.so libcoreutils.a')
        tools.AutoBuild.install (self)
        if 'BOOTSTRAP' in os.environ.keys ():
            self.system ('mkdir -p %(install_prefix)/lib')
            self.system ('cp -pv lib/libcoreutils* %(install_prefix)/lib')
