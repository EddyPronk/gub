from gub import targetbuild

### BROKEN
class Msys (targetbuild.AutoBuild):
    source = ':pserver:anonymous@mingw.cvs.sourceforge.net:/cvsroot/mingw&modulemsys/rt/src'
    def patch (self):
        self.system ('cd %(srcdir)s && dos2unix `find -type f`')
    def configure (self):
        self.shadow ()
        c = self.expand ('%(configure_command)s')
        c = c.replace ('--config-cache', '')
        self.system ('mkdir %(builddir)s ', ignore_errors=True)
        self.system ('cd  %(builddir)s && %(c)s', locals ())
        return c
    
