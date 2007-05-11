from gub import targetpackage
from gub import mirrors

class Libexif (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with (version="0.6.9", mirror=mirrors.sf)
