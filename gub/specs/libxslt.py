from gub import context
from gub import loggedos
from gub import misc
from gub import targetbuild

class Libxslt (targetbuild.AutoBuild):
    source = 'http://xmlsoft.org/sources/libxslt-1.1.24.tar.gz'
    def patch (self):
        self.system ('rm -f %(srcdir)s/libxslt/xsltconfig.h')
    def get_build_dependencies (self):
        return ['libxml2-devel', 'zlib-devel']
    def configure_command (self):
        return (targetbuild.AutoBuild.configure_command (self)
                + misc.join_lines ('''
--without-python
--without-crypto
'''))
    @context.subst_method
    def config_script (self):
        return 'xslt-config'

class Libxslt__mingw (Libxslt):
    def configure_command (self):
        return (Libxslt.configure_command (self)
                + misc.join_lines ('''
--without-plugins
'''))
