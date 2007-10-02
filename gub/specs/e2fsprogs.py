from gub import mirrors
from gub import targetbuild

http://www.eecs.harvard.edu/~nr/noweb/dist/noweb-2.11b.tgz


class E2fsprogs (targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
    source = mirrors.with_tarball (name='e2fsprogs', mirror=mirrors.sf, version='1.38')
    def install_command (self):
        return (targetbuild.TargetBuild.install_command (self)
                + ' install-libs')
