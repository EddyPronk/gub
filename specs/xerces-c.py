import download
import targetpackage

class Xerces_c (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_tarball (mirror=download.xerces_c, version='2_7_0')
