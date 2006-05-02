import download
import targetpackage

class Fondu (targetpackage.Target_package):
    def __init__ (self, settings):
        targetpackage.Target_package.__init__ (self, settings)
        self.with (version="060102",
             mirror='http://fondu.sourceforge.net/fondu_src-060102.tgz')

    def srcdir (self):
        return '%(allsrcdir)s/' + ('fondu-%s' % self.version())
    
    def patch (self):
        targetpackage.Target_package.patch (self)
        self.file_sub ([('wilprefix', 'prefix')],
               '%(srcdir)s/Makefile.in')
        
class Fondu__darwin (Fondu):
    def patch(self):
        Fondu.patch (self)
        self.file_sub ([('/System/Library/',
                '%(system_root)s/System/Library/')],
               '%(srcdir)s/Makefile.in')
        
