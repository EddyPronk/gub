from gub import misc
from gub import target
from gub import tools

class Expat (target.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/expat/expat-1.95.8.tar.gz'

    def get_build_dependencies (self):
        return ['libtool', 'tools::expat']

    def patch (self):
        self.system ("rm %(srcdir)s/configure")
        self.apply_patch ('expat-1.95.8-mingw.patch')
        self.system ("touch %(srcdir)s/tests/xmltest.sh.in")
        target.AutoBuild.patch (self)

    def configure (self):
        target.AutoBuild.configure (self)
        # # FIXME: libtool too old for cross compile
        self.update_libtool ()

    def makeflags (self):
        return misc.join_lines ('''
CFLAGS="-O2 -DHAVE_EXPAT_CONFIG_H"
EXEEXT=
RUN_FC_CACHE_TEST=false
''')
    def compile_command (self):
        return (target.AutoBuild.compile_command (self)
            + self.makeflags ())

    def install_command (self):
        return (target.AutoBuild.install_command (self)
                + self.makeflags ())

class Expat__linux__arm__vfp (Expat):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/expat/expat-2.0.0.tar.gz'
    def patch (self):
        self.system ("touch %(srcdir)s/tests/xmltest.sh.in")
        target.AutoBuild.patch (self)

class Expat__tools (tools.AutoBuild):
    patches = ['expat-1.95.8-mingw.patch']
    def get_build_dependencies (self):
        return ['libtool']
