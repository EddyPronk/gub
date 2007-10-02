from gub import targetbuild
from gub import mirrors

class Libiconv (targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
        self.with_template (version='1.11', mirror=mirrors.gnu)
    
    def force_sequential_build (self):
        return True
    
    def get_build_dependencies (self):
        return ['gettext-devel', 'libtool']

    def configure (self):
        targetbuild.TargetBuild.configure (self)
        # # FIXME: libtool too old for cross compile
        self.update_libtool ()
        
    def install (self):
        targetbuild.TargetBuild.install (self)
        self.system ('rm %(install_prefix)s/lib/charset.alias')
