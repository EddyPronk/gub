import mirrors
import targetpackage

class Libxml2 (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.gnome_218, version='2.6.27')
