from gub import mirrors
from gub import misc
from gub import repository
from gub import targetpackage

class Libdbi_drivers_sqlite3 (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        #self.with_template (version='0.8.1', mirror=mirrors.sf, format='gz')
        self.with_vc (repository.NewTarBall (self.settings.downloads, mirrors.sf, 'libdbi-drivers', '0.8.2'))

    def get_build_dependencies (self):
        return ['sqlite', 'libdbi', 'libtool']

    def get_dependency_dict (self):
        return {'': self.get_build_dependencies ()}

    def configure_command (self):
        return (targetpackage.TargetBuildSpec.configure_command (self)
                + misc.join_lines ('''
--disable-docs
--with-dbi-incdir=%(system_root)s/usr/include
--with-sqlite3
--with-sqlite3-libdir=%(system_root)s/usr/include
--with-sqlite3-incdir=%(system_root)s/usr/include
'''))

    def configure (self):
        self.system ('''
mkdir -p %(builddir)s/doc/include
cd %(builddir)s && touch doc/Makefile.in doc/include/Makefile.in
''')
        targetpackage.TargetBuildSpec.configure (self)
        self.update_libtool ()

    def makeflags (self):
        return ' doc_DATA= html_DATA='

    def compile_command (self):
        return (targetpackage.TargetBuildSpec.compile_command (self)
                + self.makeflags ())

    def install_command (self):
        return (targetpackage.TargetBuildSpec.install_command (self)
                + self.makeflags ())

class Libdbi_drivers_sqlite3__debian__arm (Libdbi_drivers_sqlite3):
    def get_build_dependencies (self):
        return ['sqlite3-dev', 'libdbi', 'libtool']

