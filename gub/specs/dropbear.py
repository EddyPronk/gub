from gub import target

class Dropbear (target.AutoBuild):
    source = 'http://matt.ucc.asn.au/dropbear/releases/dropbear-0.49.tar.gz'
    def get_subpackage_names (self):
        return ['']
    def get_build_dependencies (self):
        return ['zlib']
    def configure (self):
        target.AutoBuild.configure (self)
        self.system ('''
mkdir -p %(builddir)s/libtomcrypt/src/mac/f9
mkdir -p %(builddir)s/libtomcrypt/src/mac/xcbc
mkdir -p %(builddir)s/libtomcrypt/src/math/fp
mkdir -p %(builddir)s/libtomcrypt/src/modes/f8
mkdir -p %(builddir)s/libtomcrypt/src/modes/lrw
''')
    def makeflags (self):
        return 'PROGRAMS="dropbear dbclient dropbearkey dropbearconvert ssh scp"'
    def compile_command (self):
        return (target.AutoBuild.compile_command (self)
            + ' SCPPROGRESS=1 MULTI=1')

class Dropbear__linux__arm__vfp (Dropbear):
    def patch (self):
        Dropbear.patch (self)
        self.system ('''
cd %(srcdir)s && patch -p1 < %(patchdir)s/dropbear-random-xauth-options.h.patch
''')
