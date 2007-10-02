from gub import mirrors
from gub import targetbuild

class Hello (targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
    source = mirrors.with_tarball (name='hello', mirror=mirrors.lilypondorg, version='1.0')
