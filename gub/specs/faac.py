from gub import mirrors
from gub import targetbuild

class Faac (targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
    source = mirrors.with_tarball (name='faac', mirror=mirrors.sf, version='1.24')
