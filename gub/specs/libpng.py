from gub import mirrors
from gub import targetbuild

class Libpng (targetbuild.TargetBuild):
    source = mirrors.with_template (name='libpng', version='1.2.8', mirror=mirrors.libpng)
    def get_dependency_dict (self):
        return {'':['zlib']}
    
    def get_build_dependencies (self):
        return ['zlib-devel', 'tools::autoconf', 'tools::automake', 'tools::libtool']

    def name (self):
        return 'libpng'

    def patch (self):
        self.file_sub ([('(@INSTALL.*)@PKGCONFIGDIR@',
                r'\1${DESTDIR}@PKGCONFIGDIR@')],
               '%(srcdir)s/Makefile.in')
        self.file_sub ([('(@INSTALL.*)@PKGCONFIGDIR@',
                r'\1${DESTDIR}@PKGCONFIGDIR@')],
               '%(srcdir)s/Makefile.am')

    def configure (self):
        targetbuild.TargetBuild.configure (self)
        # # FIXME: libtool too old for cross compile
        self.update_libtool ()

    def compile_command (self):
        c = targetbuild.TargetBuild.compile_command (self)
        ## need to call twice, first one triggers spurious Automake stuff.                
        return '(%s) || (%s)' % (c,c)
    
class Libpng__mingw (Libpng):
    def xxconfigure (self):
        # libtool will not build dll if -no-undefined flag is
        # not present
        self.file_sub ([('-version-info',
                '-no-undefined -version-info')],
             '%(srcdir)s/Makefile.am')
        self.autoupdate ()
        Libpng.configure (self)

from gub import toolsbuild 

class Libpng__tools (toolsbuild.ToolsBuild, Libpng):
    source = Libpng.source
    def get_build_dependencies (self):
        return ['libtool']
    def patch (self):
        Libpng.patch (self)
