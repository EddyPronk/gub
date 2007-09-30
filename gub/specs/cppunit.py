from gub import mirrors
from gub import targetpackage

class Cppunit (targetpackage.TargetBuild):
    def __init__ (self, settings):
        targetpackage.TargetBuild.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.sf, version='1.10.2')
