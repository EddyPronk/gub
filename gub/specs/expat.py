import os
#
from gub import misc
from gub import target
from gub import tools

class Expat (target.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/expat/expat-2.0.1.tar.gz'
    patches = ['expat-2.0.1-mingw.patch']
    def _get_build_dependencies (self):
        return ['libtool', 'tools::expat']
    def patch (self):
        target.AutoBuild.patch (self)
        #FIXME: should have configure.ac/in vs configure timestamp test
        self.system ("rm %(srcdir)s/configure")
        self.system ("touch %(srcdir)s/tests/xmltest.sh.in")
    def makeflags (self):
        SHELL = ''
        if 'BOOTSTRAP' in os.environ.keys ():
            SHELL = '%(tools_prefix)s/bin/bash'
        return SHELL + misc.join_lines ('''
CFLAGS="-O2 -DHAVE_EXPAT_CONFIG_H"
EXEEXT=
RUN_FC_CACHE_TEST=false
''')

class Expat__mingw (Expat):
    def configure_variables (self):
        # mingw's expat libtool build breaks with DASH
        return (Expat.configure_variables (self)
                .replace ('SHELL=', 'XSHELL='))

class Expat__linux__arm__vfp (Expat):
    patches = []
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/expat/expat-2.0.0.tar.gz'
    def patch (self):
        self.system ("touch %(srcdir)s/tests/xmltest.sh.in")
        target.AutoBuild.patch (self)

class Expat__tools (tools.AutoBuild, Expat):
    def _get_build_dependencies (self):
        return [
            'automake',
            'libtool',
            ]
