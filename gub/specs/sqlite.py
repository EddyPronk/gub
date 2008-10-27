from gub import targetbuild

sqlite = 'http://www.sqlite.org/sqlite-%(ball_version)s.tar.%(format)s'

class Sqlite (targetbuild.AutoBuild):
    source = mirrors.with_tarball (name='sqlite', mirror=sqlite, version='3.3.16')
    def configure_command (self):
        return (targetbuild.AutoBuild.configure_command (self)
                + ' --disable-tcl --enable-threadsafe')
    def patch (self):
        open (self.expand ('%(srcdir)s/PUBLIC-DOMAIN'), 'w').write ('''
Sqlite has no license, it is in the public domain.
See http://www.sqlite.org/copyright.html .
''')
    def license_files (self):
        return ['%(srcdir)s/PUBLIC-DOMAIN']
