from gub import mirrors
from gub import targetbuild

class Fondu (targetbuild.AutoBuild):
    source = mirrors.with_template (name='fondu', version="060102",
             mirror='http://fondu.sourceforge.net/fondu_src-060102.tgz')

    def srcdir (self):
        return '%(allsrcdir)s/' + ('fondu-%s' % self.version ())

    
    def patch (self):
        targetbuild.AutoBuild.patch (self)
        self.file_sub ([('wilprefix', 'prefix')],
                       '%(srcdir)s/Makefile.in')
        
class Fondu__darwin (Fondu):
    def patch (self):
        Fondu.patch (self)
        self.file_sub ([('/System/Library/',
                '%(system_root)s/System/Library/')],
               '%(srcdir)s/Makefile.in')
        
