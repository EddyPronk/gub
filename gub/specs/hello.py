from gub import mirrors
from gub import targetbuild

class Hello (targetbuild.TargetBuild):
    def __init__ (self, settings):
        targetbuild.TargetBuild.__init__ (self, settings)
        self.with_tarball (mirror=mirrors.lilypondorg, version='1.0')
