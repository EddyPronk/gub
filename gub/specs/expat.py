from gub import mirrors
from gub import misc
from gub import targetpackage
from gub import toolpackage

class Expat (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_template (version='1.95.8', mirror=mirrors.sf, format='gz')

    def get_build_dependencies (self):
        return ['libtool']

    def patch (self):
        self.system ("rm %(srcdir)s/configure")
        self.system ("cd %(srcdir)s && patch -p1 < %(patchdir)s/expat-1.95.8-mingw.patch")
        self.system ("touch %(srcdir)s/tests/xmltest.sh.in")
        targetpackage.TargetBuildSpec.patch (self)

    def configure (self):
        targetpackage.TargetBuildSpec.configure (self)
        # # FIXME: libtool too old for cross compile
        self.update_libtool ()

    def makeflags (self):
        return misc.join_lines ('''
CFLAGS="-O2 -DHAVE_EXPAT_CONFIG_H"
EXEEXT=
RUN_FC_CACHE_TEST=false
''')
    def compile_command (self):
        return (targetpackage.TargetBuildSpec.compile_command (self)
            + self.makeflags ())

    def install_command (self):
        return (targetpackage.TargetBuildSpec.install_command (self)
                + self.makeflags ())

class Expat__linux__arm__vfp (Expat):
    def __init__ (self, settings):
        Expat.__init__ (self, settings)
        self.with_template (version='2.0.0')
    def patch (self):
        self.system ("touch %(srcdir)s/tests/xmltest.sh.in")
        targetpackage.TargetBuildSpec.patch (self)

class Expat__local (toolpackage.ToolBuildSpec):
    def __init__ (self,settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
        self.with_template (version='1.95.8', mirror=mirrors.sf, format='gz')

    def patch (self):
        toolpackage.ToolBuildSpec.patch (self)
        self.system ("cd %(srcdir)s && patch -p1 < %(patchdir)s/expat-1.95.8-mingw.patch")

    def get_build_dependencies (self):
        return ['libtool']            
