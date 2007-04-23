import download
import targetpackage

class Libxml2 (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_tarball (mirror=download.gnome_218, version='2.6.27')
