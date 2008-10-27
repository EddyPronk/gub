from gub import mirrors
from gub import targetbuild

class Faac (targetbuild.AutoBuild):
    source = mirrors.with_tarball (name='faac', mirror=mirrors.sf, version='1.24')
