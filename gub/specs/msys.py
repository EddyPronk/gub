from gub import targetbuild
from gub import repository


### BROKEN
class Msys(targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
        repo = repository.CVS (self.get_repodir(),
                               source=':pserver:anonymous@mingw.cvs.sourceforge.net:/cvsroot/mingw',
                               module='msys/rt/src'
                               )
    source = mirrors.with_vc (repo)

    def patch(self):
        self.system ('cd %(srcdir)s && dos2unix `find -type f`')
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
        
    def configure(self):
        c = self.expand ('%(configure_command)s')

        c = c.replace ('--config-cache', '')
        self.system ('mkdir %(builddir)s ', ignore_errors=True)
        self.system ('cd  %(builddir)s && %(c)s', locals())
        
        return c
    
