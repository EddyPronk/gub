from gub import target
from gub import tools

class Libt1 (target.AutoBuild):
    source = 'ftp://sunsite.unc.edu/pub/Linux/libs/graphics/t1lib-5.1.2.tar.gz'
    def _get_build_dependencies (self):
        return [
            'tools::libtool',
            ]
    def force_sequential_build (self):
        return True
    def configure (self):
        self.shadow ()
        tools.AutoBuild.configure (self)
    def makeflags (self):
        return ''' without_doc 'VPATH:=$(srcdir)' '''

class Libt1__tools (tools.AutoBuild, Libt1):
    def _get_build_dependencies (self):
        return [
            'libtool',
            ]
    def configure (self):
        self.shadow ()
        tools.AutoBuild.configure (self)
