from gub import misc
from gub import target

class Libdbi_drivers_sqlite3 (target.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/libdbi-drivers/libdbi-drivers-0.8.2.tar.gz'
    def _get_build_dependencies (self):
        return ['sqlite-devel', 'libdbi-devel', 'libtool']
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + misc.join_lines ('''
--disable-docs
--with-dbi-incdir=%(system_prefix)s/include
--with-sqlite3
--with-sqlite3-libdir=%(system_prefix)s/include
--with-sqlite3-incdir=%(system_prefix)s/include
'''))

    def configure (self):
        self.system ('''
mkdir -p %(builddir)s/doc/include
cd %(builddir)s && touch doc/Makefile.in doc/include/Makefile.in
''')
        target.AutoBuild.configure (self)

    def makeflags (self):
        return ' doc_DATA= html_DATA='

    def compile_command (self):
        return (target.AutoBuild.compile_command (self)
                + self.makeflags ())

    def install_command (self):
        return (target.AutoBuild.install_command (self)
                + self.makeflags ())

class Libdbi_drivers_sqlite3__debian__arm (Libdbi_drivers_sqlite3):
    def get_build_dependencies (self):
        return ['sqlite3-dev', 'libdbi', 'libtool']

