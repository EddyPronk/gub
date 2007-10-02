from gub import mirrors
from gub import targetbuild

class Cppunit (targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
    source = mirrors.with_tarball (name='cppunit', mirror=mirrors.sf, version='1.10.2')
