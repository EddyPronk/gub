from gub import target as tools

'''
Build shared libcoreutils.so without using libtool
for GUB's librestrict(2) to kick-in.
'''

class Coreutils__tools (tools.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/coreutils/coreutils-6.12.tar.gz'
    patches = ['coreutils-6.12-shared.patch']
    def force_autoupdate (self):
        return True
    def autoupdate (self):
        self.system ('''
cd %(srcdir)s && autoreconf
''')
    def configure_command (self):
        return (tools.AutoBuild.configure_command (self)
                + ' CFLAGS=-fPIC')
    def makeflags (self):
        return ''' LDFLAGS='%(rpath)s' LIBS='$(cp_LDADD) $(ls_LDADD)' RANLIB='mvaso () { mv $$1 $$(dirname $$1)/$$(basename $$1 .a).so; }; mvaso ' libcoreutils_a_AR='gcc -shared -o' '''
    def wrap_executables (self):
        return False
    def install (self):
        # The RANLIB/mvaso trick needs libcoreutils.a to exist at install time.
        self.system ('cd %(builddir)s/lib && ln libcoreutils.so libcoreutils.a')
        tools.AutoBuild.install (self)
