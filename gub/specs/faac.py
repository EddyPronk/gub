from gub import mirrors
from gub import targetbuild

class Faac (targetbuild.TargetBuild):
    def __init__ (self, settings):
        targetbuild.TargetBuild.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.sf, version='1.24')
