import targetpackage

class Libiconv (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with (version='1.9.2')
    
    def broken_for_distcc (self):
        return True
    
    def get_build_dependencies (self):
        return ['gettext-devel', 'libtool']

    def configure (self):
        targetpackage.TargetBuildSpec.configure (self)
        # # FIXME: libtool too old for cross compile
        self.update_libtool ()
    def install (self):
        targetpackage.TargetBuildSpec.install (self)
        self.system ('rm %(install_root)s/usr/lib/charset.alias')
        
