from gub import mirrors
from gub import targetbuild

class Hello (targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
        self.with_tarball (mirror=mirrors.lilypondorg, version='1.0')
