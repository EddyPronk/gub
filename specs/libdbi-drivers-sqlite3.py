import download
import misc
import repository
import targetpackage

class Libdbi_drivers_sqlite3 (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        #self.with (version='0.8.1', mirror=download.sf, format='gz')
        self.with_vc (repository.NewTarBall (self.settings.downloads, download.sf, 'libdbi-drivers', '0.8.2'))

    def get_build_dependencies (self):
        return ['sqlite', 'libdbi', 'libtool']

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
cd %(builddir)s && mkdir -p doc/include
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

    def install (self):
        targetpackage.TargetBuildSpec.install (self)
        self.system ('''mv %(install_root)s/usr/lib/dbd/libsqlite3.so %(install_root)s/usr/lib/dbd/libdbdsqlite3.so''')

class Libdbi_drivers_sqlite3__debian__arm (Libdbi_drivers_sqlite3):
    def get_build_dependencies (self):
        return ['sqlite3-dev', 'libdbi', 'libtool']

