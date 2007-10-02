from gub import mirrors
from gub import targetbuild

class Hello (targetbuild.TargetBuild):
    source = mirrors.with_tarball (name='hello', mirror=mirrors.lilypondorg, version='1.0')
