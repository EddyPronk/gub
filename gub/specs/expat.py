from gub import misc
from gub import target
from gub import tools

class Expat (target.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/expat/expat-1.95.8.tar.gz'
    patches = ['expat-1.95.8-mingw.patch']

    def _get_build_dependencies (self):
        return ['libtool', 'tools::expat']

    def patch (self):
        target.AutoBuild.patch (self)
        #FIXME: should have configure.ac/in vs configure timestamp test
        self.system ("rm %(srcdir)s/configure")
        self.system ("touch %(srcdir)s/tests/xmltest.sh.in")

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
    source = Expat.source
    patches = Expat.patches
    def _get_build_dependencies (self):
        return ['libtool']
