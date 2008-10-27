from gub import mirrors
from gub import targetbuild

class Hello (targetbuild.AutoBuild):
    source = mirrors.with_tarball (name='hello', mirror=mirrors.lilypondorg, version='1.0')
