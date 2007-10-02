from gub import mirrors
from gub import targetbuild

class Libxml2 (targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
        self.with_tarball (mirror=mirrors.gnome_218, version='2.6.27')
    def configure_command (self):
        return (targetbuild.TargetBuild.configure_command (self)
                + ' --without-python')
