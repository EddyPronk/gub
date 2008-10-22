from gub import context
from gub import misc
from gub import targetbuild

class Libunicows (targetbuild.TargetBuild):
    source = 'http://surfnet.dl.sourceforge.net/libunicows/libunicows-1.1.2-src.tar.gz'
    def install (self):
        self.system ('mkdir -p %(install_prefix)s/lib %(install_prefix)s/bin')
        self.system ('cp %(builddir)s/lib/mingw32/*.a %(install_prefix)s/lib')
    def configure (self):
        pass
    def patch (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')

class Libunicows__mingw (Libunicows):
    def makeflags (self):
        return misc.join_lines ('''-C src -f makefile.mingw32
AR=%(toolchain_prefix)sar
CC=%(toolchain_prefix)sgcc
LD=%(toolchain_prefix)sld
PATHSEP=/
RANLIB=%(toolchain_prefix)sranlib
STRIP=%(toolchain_prefix)sstrip
''')
    def foebar (self):
        return misc.join_lines ('''-C src -f makefile.mingw32
AR=%(AR)s
CC=%(CC)s
LD=%(LD)s
PATHSEP=/
RANLIB=%(RANLIB)s
STRIP=%(STRIP)s
''')
