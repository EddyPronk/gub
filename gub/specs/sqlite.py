from gub import misc
from gub import target

class Sqlite (target.AutoBuild):
    source = 'http://www.sqlite.org/sqlite-3.6.4.tar.gz' # 3.3.16
    configure_flags = (target.AutoBuild.configure_flags
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
    configure_flags = ('config_TARGET_EXEEXT=.exe '
                + Sqlite.configure_flags
                .replace ('--enable-threadsafe', '--disable-threadsafe'))
