import download
import misc
import targetpackage
import toolpackage

class Expat (targetpackage.Target_package):
    def __init__ (self, settings):
        targetpackage.Target_package.__init__ (self, settings)
        self.with (version='1.95.8', mirror=download.sf, format='gz')

    def get_build_dependencies (self):
        return ['libtool']

    def patch (self):
        targetpackage.Target_package.patch (self)
        self.system ("cd %(srcdir)s && patch -p1 < %(patchdir)s/expat-1.95.8-mingw.patch")

    def configure (self):
        targetpackage.Target_package.configure (self)
        # # FIXME: libtool too old for cross compile
        self.update_libtool ()

    def makeflags (self):
        return misc.join_lines ('''
CFLAGS="-O2 -DHAVE_EXPAT_CONFIG_H"
EXEEXT=
RUN_FC_CACHE_TEST=false
''')
    def compile_command (self):
        return (targetpackage.Target_package.compile_command (self)
            + self.makeflags ())

    def install_command (self):
        return (targetpackage.Target_package.install_command (self)
            + self.makeflags ())

class Expat__local (toolpackage.ToolBuildSpecification):
    def __init__ (self,settings):
        toolpackage.ToolBuildSpecification.__init__ (self, settings)
        self.with (version='1.95.8', mirror=download.sf, format='gz')
