from gub import targetbuild
from gub import repository


### BROKEN
class Msys(targetbuild.TargetBuild):
    source = mirrors.with_vc (repository.CVS (None,
                               source=':pserver:anonymous@mingw.cvs.sourceforge.net:/cvsroot/mingw',
                               module='msys/rt/src'))

    def patch(self):
        self.system ('cd %(srcdir)s && dos2unix `find -type f`')
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
        
    def configure(self):
        c = self.expand ('%(configure_command)s')

        c = c.replace ('--config-cache', '')
        self.system ('mkdir %(builddir)s ', ignore_errors=True)
        self.system ('cd  %(builddir)s && %(c)s', locals())
        
        return c
    
