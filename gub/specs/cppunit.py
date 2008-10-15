from gub import mirrors
from gub import targetbuild

class Cppunit (targetbuild.TargetBuild):
    source = mirrors.with_tarball (name='cppunit', mirror=mirrors.sf, version='1.10.2')
