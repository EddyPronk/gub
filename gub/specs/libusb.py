from gub import targetpackage
from gub import mirrors

class Libusb (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with (version="0.1.12", mirror=mirrors.sf)
