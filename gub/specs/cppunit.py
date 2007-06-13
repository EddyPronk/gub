from gub import mirrors
from gub import targetpackage

class Cppunit (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.sf, version='1.10.2')
