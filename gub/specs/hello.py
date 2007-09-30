from gub import mirrors
from gub import targetpackage

class Hello (targetpackage.TargetBuild):
    def __init__ (self, settings):
        targetpackage.TargetBuild.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.lilypondorg, version='1.0')
