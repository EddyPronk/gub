import mirrors
import targetpackage

class Libpng (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with (version='1.2.8', mirror=mirrors.libpng)

    def license_file (self):
        return '%(srcdir)s/LICENSE' 

    def get_dependency_dict (self):
        return {'':['zlib']}
    
    def get_build_dependencies (self):
        return ['zlib-devel']

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
        targetpackage.TargetBuildSpec.configure (self)
        # # FIXME: libtool too old for cross compile
        self.update_libtool ()

    def compile_command (self):
        c = targetpackage.TargetBuildSpec.compile_command (self)
        ## need to call twice, first one triggers spurious Automake stuff.                
        return '(%s) || (%s)' % (c,c)
    
class Libpng__mingw (Libpng):
    def configure (self):
        # libtool will not build dll if -no-undefined flag is
        # not present
        self.file_sub ([('-version-info',
                '-no-undefined -version-info')],
             '%(srcdir)s/Makefile.am')
        self.autoupdate ()
        Libpng.configure (self)

import toolpackage 

class Libpng__local (toolpackage.ToolBuildSpec, Libpng):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
        self.with (version='1.2.8', mirror=mirrors.libpng)

    def get_build_dependencies (self):
        return ['libtool']

    def patch (self):
        Libpng.patch (self)

    # FIXME, mi-urg?
    def license_file (self):
        return Libpng.license_file (self)

