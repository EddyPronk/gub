from gub import target
from gub import tools 

class Libpng (target.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/libpng/libpng-1.2.8-config.tar.gz'
    patches = ['libpng-pngconf.h-setjmp.patch']
    def get_dependency_dict (self):
        return {'':['zlib']}
    
    def get_build_dependencies (self):
        return ['zlib-devel', 'tools::autoconf', 'tools::automake', 'tools::libtool']

    def name (self):
        return 'libpng'

    def patch (self):
        target.AutoBuild.patch (self)
        self.file_sub ([('(@INSTALL.*)@PKGCONFIGDIR@',
                r'\1${DESTDIR}@PKGCONFIGDIR@')],
               '%(srcdir)s/Makefile.in')
        self.file_sub ([('(@INSTALL.*)@PKGCONFIGDIR@',
                r'\1${DESTDIR}@PKGCONFIGDIR@')],
               '%(srcdir)s/Makefile.am')

    def compile_command (self):
        c = target.AutoBuild.compile_command (self)
        ## need to call twice, first one triggers spurious Automake stuff.                
        return '(%s) || (%s)' % (c,c)
    
class Libpng__tools (tools.AutoBuild, Libpng):
    source = Libpng.source
    patches = Libpng.patches
    def get_build_dependencies (self):
        return ['libtool']
    def patch (self):
        Libpng.patch (self)
