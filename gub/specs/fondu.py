from gub import mirrors
from gub import targetpackage

class Fondu (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with (version="060102",
             mirror='http://fondu.sourceforge.net/fondu_src-060102.tgz')

    def srcdir (self):
        return '%(allsrcdir)s/' + ('fondu-%s' % self.version())

    def license_file (self):
        return '%(srcdir)s/LICENSE'
    
    def patch (self):
        targetpackage.TargetBuildSpec.patch (self)
        self.file_sub ([('wilprefix', 'prefix')],
                       '%(srcdir)s/Makefile.in')
        
class Fondu__darwin (Fondu):
    def patch(self):
        Fondu.patch (self)
        self.file_sub ([('/System/Library/',
                '%(system_root)s/System/Library/')],
               '%(srcdir)s/Makefile.in')
        
