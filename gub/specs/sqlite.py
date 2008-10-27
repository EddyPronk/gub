from gub import misc
from gub import targetbuild

class Sqlite (targetbuild.AutoBuild):
    source = 'http://www.sqlite.org/sqlite-3.6.4.tar.gz' # 3.3.16
    def configure_command (self):
        return (targetbuild.AutoBuild.configure_command (self)
                + misc.join_lines ('''
--disable-tcl
--enable-threadsafe
'''))
    def patch (self):
        self.dump ('''
Sqlite has no license, it is in the public domain.
See http://www.sqlite.org/copyright.html .
''',
            '%(srcdir)s/PUBLIC-DOMAIN')
    def license_files (self):
        return ['%(srcdir)s/PUBLIC-DOMAIN']

class Sqlite__mingw (Sqlite):
    def configure_command (self):
        return ('config_TARGET_EXEEXT=.exe '
                + Sqlite.configure_command (self).replace ('--enable-threadsafe', '--disable-threadsafe'))
