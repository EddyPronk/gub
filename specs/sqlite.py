import targetpackage

sqlite = 'http://www.sqlite.org/sqlite-%(ball_version)s.tar.%(format)s'

class Sqlite (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_tarball (mirror=sqlite, version='3.3.16')
    def configure_command (self):
        return (targetpackage.TargetBuildSpec.configure_command (self)
                + ' --disable-tcl --enable-threadsafe')
    def patch (self):
        open (self.expand ('%(srcdir)s/PUBLIC-DOMAIN'), 'w').write ('''
Sqlite has no license, it is in the public domain.
See http://www.sqlite.org/copyright.html .
''')
    def license_file (self):
        return '%(srcdir)s/PUBLIC-DOMAIN'
